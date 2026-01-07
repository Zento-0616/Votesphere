import sys
import os
import socket
import webbrowser
import io
from threading import Timer
from datetime import datetime
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import mysql.connector
from mysql.connector import Error


# --- FIX PATHS FOR PYINSTALLER (.exe support) ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace("\\", "/")


app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

app.secret_key = "vote_sphere_secret_key"

# --- MYSQL CONFIGURATION ---
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'votesphere',
    'autocommit': True,
    'connect_timeout': 10
}


def get_db_connection():
    """
    Self-Healing Connection:
    Tries to connect and returns None if XAMPP is offline.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except:
        return None
    return None


def is_election_active(conn):
    try:
        # buffered=True is critical for MySQL in a web environment
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT `value` FROM `system_config` WHERE `key`='election_status'")
        status = cursor.fetchone()

        if not status or status['value'] != 'active':
            cursor.close()
            return False, "Election is manually closed."

        cursor.execute("SELECT `value` FROM `system_config` WHERE `key`='election_target_time'")
        target_str = cursor.fetchone()
        cursor.close()

        if target_str and target_str['value']:
            target_time = datetime.fromisoformat(target_str['value'])
            if datetime.now() > target_time:
                return False, "Election time has ended."
        return True, "Active"
    except Exception as e:
        return False, "Database check error."


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            return render_template('login.html', error="❌ Database Offline. Start MySQL in XAMPP.")

        active, msg = is_election_active(conn)
        if not active:
            conn.close()
            return render_template('login.html', error=f"⛔ {msg}")

        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute('SELECT * FROM `users` WHERE `username` = %s AND `password` = %s', (username, password))
            user = cursor.fetchone()

            if user:
                if user['role'] != 'voter':
                    return render_template('login.html', error="⚠️ Admin accounts cannot vote here.")
                elif user['voted']:
                    return render_template('login.html', error="✅ You have already voted.")
                else:
                    new_token = str(uuid.uuid4())
                    cursor.execute("UPDATE `users` SET `session_token` = %s, `last_active` = NOW() WHERE `id` = %s",
                                   (new_token, user['id']))
                    conn.commit()
                    session['user_id'] = user['id']
                    session['full_name'] = user['full_name']
                    session['token'] = new_token
                    return redirect(url_for('vote'))
            else:
                return render_template('login.html', error="❌ Invalid ID or Password")
        finally:
            if 'cursor' in locals(): cursor.close()
            if conn: conn.close()

    return render_template('login.html')


@app.route('/candidate_image/<int:candidate_id>')
def get_candidate_image(candidate_id):
    conn = get_db_connection()
    if not conn: return ""
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT `image` FROM `candidates` WHERE `id` = %s", (candidate_id,))
        row = cursor.fetchone()
        if row and row[0]:
            return send_file(io.BytesIO(row[0]), mimetype='image/png')
        return send_file(resource_path('static/default.png'), mimetype='image/png')
    except:
        return ""
    finally:
        if 'cursor' in locals(): cursor.close()
        if conn: conn.close()


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return "Database Error: Connection lost. Please refresh."

    try:
        cursor = conn.cursor(dictionary=True, buffered=True)

        if request.method == 'POST':
            # Double check election status
            active, msg = is_election_active(conn)
            if not active:
                return jsonify({"status": "error", "message": msg})

            # Check if user already voted
            cursor.execute("SELECT voted FROM users WHERE id = %s", (session['user_id'],))
            check = cursor.fetchone()
            if check and check['voted']:
                return jsonify({"status": "error", "message": "You have already voted."})

            # Process the votes
            for position, candidate_id in request.form.items():
                cursor.execute("INSERT INTO `votes` (`voter_id`, `candidate_id`, `position`) VALUES (%s, %s, %s)",
                               (session['user_id'], candidate_id, position))
                cursor.execute("UPDATE `candidates` SET `votes` = `votes` + 1 WHERE `id` = %s", (candidate_id,))

            cursor.execute("UPDATE `users` SET `voted` = 1 WHERE `id` = %s", (session['user_id'],))
            cursor.execute("INSERT INTO `audit_trail` (user, module, action, description) VALUES (%s, %s, %s, %s)",
                           (session['full_name'], 'Election', 'Mobile Vote', f"Voted successfully"))

            conn.commit()
            session.clear()
            return jsonify({"status": "success", "message": "Vote Submitted!"})

        # FETCH DATA FOR UI
        cursor.execute("SELECT DISTINCT `position` FROM `candidates` ORDER BY `position` ASC")
        positions = [row['position'] for row in cursor.fetchall()]

        candidates_by_pos = {}
        for pos in positions:
            cursor.execute("SELECT `id`, `name`, `grade`, `votes` FROM `candidates` WHERE `position` = %s", (pos,))
            candidates_by_pos[pos] = cursor.fetchall()

        cursor.execute("SELECT `value` FROM `system_config` WHERE `key`='election_target_time'")
        time_row = cursor.fetchone()
        remaining = 0
        if time_row and time_row['value']:
            try:
                target = datetime.fromisoformat(time_row['value'])
                remaining = int((target - datetime.now()).total_seconds())
            except:
                pass

        return render_template('vote.html',
                               grouped_candidates=candidates_by_pos,
                               voter_name=session['full_name'],
                               remaining_seconds=remaining)
    finally:
        if 'cursor' in locals(): cursor.close()
        if conn: conn.close()


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE `users` SET `last_active` = NOW() WHERE `id` = %s", (session['user_id'],))
                conn.commit()
                cursor.close()
            finally:
                conn.close()
    return '', 204


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- HELPER FUNCTIONS FOR AUTO-IP ---
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def open_browser(url):
    webbrowser.open_new(url)


if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5050
    url = f"http://{local_ip}:{port}"

    print(f"\n🚀 VOTESPHERE LIVE: {url}\n")

    # Start browser for the local machine
    Timer(1.5, open_browser, [url]).start()

    # host='0.0.0.0' is critical so other devices can connect
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)