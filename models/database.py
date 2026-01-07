import mysql.connector
from mysql.connector import Error, errorcode

class Database:
    def __init__(self):
        self.conn = None
        self.db_name = 'votesphere'
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'raise_on_warnings': False,
            'autocommit': True,
            'connect_timeout': 10
        }
        self.first_time_setup()

    def first_time_setup(self):
        try:
            server_conn = mysql.connector.connect(**self.config)
            cursor = server_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            cursor.close()
            server_conn.close()
            self.connect()
            if self.conn:
                self.init_db()
        except Error as e:
            print(f"Setup Error: {e}")

    def connect(self):
        try:
            full_config = self.config.copy()
            full_config['database'] = self.db_name
            self.conn = mysql.connector.connect(**full_config)
            return True
        except Error:
            self.conn = None
            return False

    def get_connection(self):
        if self.conn is None or not self.conn.is_connected():
            self.connect()
        else:
            self.conn.ping(reconnect=True, attempts=3, delay=1)
        return self.conn

    def init_db(self):
        conn = self.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(buffered=True)
            tables = [
                "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, password TEXT, role VARCHAR(50), full_name VARCHAR(255), grade VARCHAR(50), section VARCHAR(50), voted TINYINT(1) DEFAULT 0, session_token VARCHAR(255), last_active DATETIME) ENGINE=InnoDB;",
                "CREATE TABLE IF NOT EXISTS candidates (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), position VARCHAR(255), grade VARCHAR(50), votes INT DEFAULT 0, image LONGBLOB) ENGINE=InnoDB;",
                "CREATE TABLE IF NOT EXISTS votes (id INT AUTO_INCREMENT PRIMARY KEY, voter_id INT, candidate_id INT, position VARCHAR(255), timestamp DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB;",
                "CREATE TABLE IF NOT EXISTS system_config (`key` VARCHAR(100) PRIMARY KEY, value TEXT) ENGINE=InnoDB;"
            ]
            for q in tables: cursor.execute(q)
            cursor.execute("INSERT IGNORE INTO users (username, password, role, full_name) VALUES ('admin', 'admin123', 'admin', 'System Administrator')")
            defaults = [('election_name', 'School Election 2025'), ('election_status', 'inactive'), ('min_app_version', '2.3')]
            for k, v in defaults: cursor.execute("INSERT IGNORE INTO system_config (`key`, value) VALUES (%s, %s)", (k, v))
            cursor.close()
        except Error as e: print(e)

    def get_config(self, key):
        conn = self.get_connection()
        if not conn: return None
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_config WHERE `key`=%s", (key,))
        res = cursor.fetchone()
        cursor.close()
        return res[0] if res else None

    def update_config(self, key, value):
        conn = self.get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO system_config (`key`, value) VALUES (%s, %s)", (key, str(value)))
        cursor.close()

    def is_version_valid(self, version):
        req = self.get_config('min_app_version')
        if not req: return True
        try: return float(version) >= float(req)
        except: return True