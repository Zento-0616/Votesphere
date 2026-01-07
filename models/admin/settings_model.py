import socket
import threading

class SettingsModel:
    def __init__(self, db):
        self.db = db
        self.server_active = False
        self.server_thread = None

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def update_admin_password(self, new_password):
        cursor = self.db.get_connection().cursor()
        cursor.execute("UPDATE users SET password = %s WHERE role = 'admin'", (new_password,))
        self.db.conn.commit()
        cursor.close()

    def get_archive_data(self, category):
        cursor = self.db.get_connection().cursor(buffered=True)
        if category == "voters":
            cursor.execute("DELETE FROM deleted_users WHERE deleted_at < DATE_SUB(NOW(), INTERVAL 30 DAY)")
            cursor.execute("SELECT username, full_name, grade, deleted_at FROM deleted_users ORDER BY deleted_at DESC")
        else:
            cursor.execute("DELETE FROM deleted_candidates WHERE deleted_at < DATE_SUB(NOW(), INTERVAL 30 DAY)")
            cursor.execute("SELECT name, position, deleted_at FROM deleted_candidates ORDER BY deleted_at DESC")
        data = cursor.fetchall()
        cursor.close()
        return data

    def restore_item(self, category, identifier):
        if category == "voters":
            self.db.restore_voter(identifier)
        else:
            self.db.restore_candidate(identifier)

    def start_portal_server(self, app_instance, port=5050):
        if not self.server_active:
            try:
                self.server_thread = threading.Thread(
                    target=lambda: app_instance.run(host='0.0.0.0', port=port, debug=False, use_reloader=False),
                    daemon=True
                )
                self.server_thread.start()
                self.server_active = True
                return True
            except:
                return False
        return True