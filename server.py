from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import sqlite3
import io
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = "vote_sphere_secret_key"
DB_NAME = "votesphere.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def is_election_active(conn):
    status = conn.execute("SELECT value FROM system_config WHERE key='election_status'").fetchone()
    if not status or status['value'] != 'active':
        return False, "Election is manually closed."

    target_str = conn.execute("SELECT value FROM system_config WHERE key='election_target_time'").fetchone()
    if target_str and target_str['value']:
        try:
            target_time = datetime.fromisoformat(target_str['value'])
            if datetime.now() > target_time:
                conn.execute("UPDATE system_config SET value='inactive' WHERE key='election_status'")
                conn.commit()
                return False, "Election time has ended."
        except ValueError:
            return False, "Invalid time format."

    return True, "Active"


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        active, msg = is_election_active(conn)

        if not active:
            flash(f"⛔ {msg}", "error")
            conn.close()
            return render_template('login.html')

        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()

        if user:

            if user['role'] == 'voter' and user['last_active']:
                try:

                    last_active = datetime.strptime(user['last_active'], '%Y-%m-%d %H:%M:%S')


                    if datetime.utcnow() - last_active < timedelta(seconds=15):
                        flash("⛔ Account is currently active on another device. Please wait.", "error")
                        conn.close()
                        return render_template('login.html')
                except Exception as e:
                    print(f"Time parsing error: {e}")


            if user['role'] != 'voter':
                flash("⚠️ Admin accounts cannot vote here.", "error")
            elif user['voted']:
                flash("✅ You have already voted.", "success")
            else:

                new_token = str(uuid.uuid4())
                conn.execute("UPDATE users SET session_token = ?, last_active = CURRENT_TIMESTAMP WHERE id = ?",
                             (new_token, user['id']))
                conn.commit()

                session['user_id'] = user['id']
                session['full_name'] = user['full_name']
                session['token'] = new_token

                conn.close()
                return redirect(url_for('vote'))
        else:
            flash("❌ Invalid ID or Password", "error")

        conn.close()

    return render_template('login.html')


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    if 'user_id' in session:
        try:
            conn = get_db_connection()

            conn.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?", (session['user_id'],))
            conn.commit()
            conn.close()
            return jsonify({'status': 'ok'})
        except:
            return jsonify({'status': 'error'}), 500
    return jsonify({'status': 'error'}), 403


@app.route('/candidate_image/<int:candidate_id>')
def get_candidate_image(candidate_id):
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT image FROM candidates WHERE id = ?", (candidate_id,)).fetchone()

        if row and row['image']:
            return send_file(io.BytesIO(row['image']), mimetype='image/png')
        else:
            return redirect(url_for('static', filename='default.png'))
    except Exception as e:
        print(f"Image error: {e}")
        return redirect(url_for('static', filename='default.png'))
    finally:
        conn.close()


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session: return redirect(url_for('login'))

    conn = get_db_connection()


    user_row = conn.execute("SELECT session_token FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    if not user_row or user_row['session_token'] != session.get('token'):
        session.clear()
        conn.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": "Session Expired: You logged in on another device."})
        flash("⚠️ You were logged out because this account logged in on another device.", "error")
        return redirect(url_for('login'))



    active, msg = is_election_active(conn)
    if not active:
        session.clear()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": msg})
        flash(f"⛔ {msg}", "error")
        return redirect(url_for('login'))


    user_check = conn.execute('SELECT voted FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user_check['voted']:
        session.clear()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "error", "message": "You have already voted."})
        flash("You have already voted.", "success")
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            for position, candidate_id in request.form.items():
                conn.execute("INSERT INTO votes (voter_id, candidate_id, position) VALUES (?, ?, ?)",
                             (session['user_id'], candidate_id, position))
                conn.execute("UPDATE candidates SET votes = votes + 1 WHERE id = ?", (candidate_id,))

            conn.execute("UPDATE users SET voted = 1 WHERE id = ?", (session['user_id'],))
            conn.commit()
            conn.execute("INSERT INTO audit_trail (user, action) VALUES (?, ?)",
                         (f"Mobile_User_{session['user_id']}", "Submitted votes via Mobile"))
            conn.commit()

            session.clear()
            return jsonify({"status": "success", "message": "Vote Submitted Successfully!"})

        except Exception as e:
            conn.rollback()
            return jsonify({"status": "error", "message": str(e)})
        finally:
            conn.close()


    positions_raw = conn.execute("SELECT DISTINCT position FROM candidates ORDER BY position").fetchall()
    positions = [row['position'] for row in positions_raw]

    candidates_by_pos = {}
    for pos in positions:
        cands = conn.execute("SELECT id, name, position, grade FROM candidates WHERE position = ?", (pos,)).fetchall()
        candidates_by_pos[pos] = cands


    target_row = conn.execute("SELECT value FROM system_config WHERE key='election_target_time'").fetchone()
    remaining_seconds = -1

    if target_row and target_row['value']:
        try:
            target_dt = datetime.fromisoformat(target_row['value'])
            now = datetime.now()
            remaining_seconds = (target_dt - now).total_seconds()
        except Exception as e:
            print(f"Time calculation error: {e}")

    conn.close()

    return render_template('vote.html',
                           grouped_candidates=candidates_by_pos,
                           voter_name=session['full_name'],
                           remaining_seconds=remaining_seconds)



@app.route('/logout')
def logout():
    if 'user_id' in session:
        try:
            conn = get_db_connection()

            conn.execute("UPDATE users SET last_active = NULL WHERE id = ?", (session['user_id'],))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logout Error: {e}")

    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)