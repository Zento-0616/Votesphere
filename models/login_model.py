import uuid
from datetime import datetime

class LoginModel:
    def __init__(self, db):
        self.db = db

    def authenticate(self, username, password):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT id, username, password, role, voted, last_active FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        return user

    def check_session_conflict(self, last_active):
        if not last_active: return False
        if isinstance(last_active, str):
            try: last_active = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S')
            except: return False
        return (datetime.now() - last_active).total_seconds() < 15

    def create_session(self, user_id):
        token = str(uuid.uuid4())
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET session_token=%s, last_active=NOW() WHERE id=%s", (token, user_id))
        self.db.conn.commit()
        cursor.close()
        return token