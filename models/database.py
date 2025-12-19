import sqlite3
import os


class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'votesphere.db')

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        try:
            self.create_tables(self.conn)
            self.run_migrations(self.conn)
            self.insert_default_data(self.conn)
        except Exception as e:
            print(f"Database Initialization Error: {e}")

    def create_tables(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                full_name TEXT,
                grade TEXT,
                section TEXT,
                voted BOOLEAN DEFAULT FALSE,
                session_token TEXT,
                last_active DATETIME
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                position TEXT,
                grade TEXT,
                votes INTEGER DEFAULT 0,
                image BLOB
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER,
                candidate_id INTEGER,
                position TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user TEXT,
                module TEXT,
                action TEXT,
                description TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_users (
                id INTEGER, username TEXT, full_name TEXT, role TEXT, 
                grade TEXT, section TEXT, deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_candidates (
                id INTEGER, name TEXT, position TEXT, grade TEXT, 
                image BLOB, deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_trail(timestamp)")
        conn.commit()

    def run_migrations(self, conn):
        cursor = conn.cursor()
        migrations = [
            ("candidates", "image", "BLOB"),
            ("users", "session_token", "TEXT"),
            ("users", "last_active", "DATETIME"),
            ("audit_trail", "module", "TEXT"),
            ("audit_trail", "description", "TEXT"),
            ("deleted_users", "grade", "TEXT"),
            ("deleted_users", "section", "TEXT"),
            ("deleted_candidates", "grade", "TEXT"),
            ("deleted_candidates", "image", "BLOB")
        ]

        for table, column, dtype in migrations:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {dtype}")
            except sqlite3.OperationalError:
                pass
        conn.commit()

    def insert_default_data(self, conn):
        cursor = conn.cursor()
        # Admin
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                           ("admin", "admin123", "admin", "System Administrator"))

        # Default Settings
        defaults = {
            'election_name': 'School Election 2025',
            'election_date': '2025-12-19',
            'election_status': 'inactive',
            'election_duration': '3600',
            'election_target_time': ''
        }
        for k, v in defaults.items():
            cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES (?, ?)", (k, v))
        conn.commit()


    def log_audit(self, user, action, module="System", description=""):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO audit_trail (user, module, action, description) VALUES (?, ?, ?, ?)",
                         (user, module, action, description))

    def get_config(self, key):
        with self.get_connection() as conn:
            res = conn.execute("SELECT value FROM system_config WHERE key=?", (key,)).fetchone()
            return res[0] if res else None

    def update_config(self, key, value):
        with self.get_connection() as conn:
            conn.execute("REPLACE INTO system_config (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def get_audit_logs(self):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT timestamp, user, module, action, description FROM audit_trail ORDER BY timestamp DESC LIMIT 200").fetchall()

    def archive_voter(self, user_id):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO deleted_users (id, username, full_name, role, grade, section) 
                SELECT id, username, full_name, role, grade, section FROM users WHERE id = ?
            """, (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

    def restore_voter(self, username):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO users (username, full_name, role, grade, section, password)
                SELECT username, full_name, role, grade, section, username FROM deleted_users WHERE username = ?
            """, (username,))
            conn.execute("DELETE FROM deleted_users WHERE username = ?", (username,))
            conn.commit()

    def archive_candidate(self, cand_id):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO deleted_candidates (id, name, position, grade, image) 
                SELECT id, name, position, grade, image FROM candidates WHERE id = ?
            """, (cand_id,))
            conn.execute("DELETE FROM candidates WHERE id = ?", (cand_id,))
            conn.commit()

    def restore_candidate(self, name):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO candidates (name, position, grade, image)
                SELECT name, position, grade, image FROM deleted_candidates WHERE name = ?
            """, (name,))
            conn.execute("DELETE FROM deleted_candidates WHERE name = ?", (name,))
            conn.commit()

    def get_archives(self, category="voters"):
        with self.get_connection() as conn:
            if category == "voters":
                conn.execute("DELETE FROM deleted_users WHERE deleted_at < date('now', '-30 days')")
                return conn.execute(
                    "SELECT username, full_name, grade, section, deleted_at FROM deleted_users ORDER BY deleted_at DESC").fetchall()
            else:
                conn.execute("DELETE FROM deleted_candidates WHERE deleted_at < date('now', '-30 days')")
                return conn.execute(
                    "SELECT name, position, grade, deleted_at FROM deleted_candidates ORDER BY deleted_at DESC").fetchall()

    def reset_election_data(self):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM votes")
            conn.execute("UPDATE candidates SET votes = 0")
            conn.execute("UPDATE users SET voted = 0")
            conn.commit()

    def check_user_voted(self, user_id):
        with self.get_connection() as conn:
            res = conn.execute("SELECT voted FROM users WHERE id=?", (user_id,)).fetchone()
            return res[0] if res else True