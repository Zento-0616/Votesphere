import sqlite3
import mysql.connector


def migrate():
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect('votesphere.db')
    sqlite_cursor = sqlite_conn.cursor()

    print("Connecting to XAMPP MySQL...")
    mysql_conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='votesphere'
    )
    mysql_cursor = mysql_conn.cursor()

    tables = ['users', 'candidates', 'votes', 'audit_trail', 'system_config']

    for table in tables:
        print(f"Migrating table: {table}...")

        try:
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            if not rows:
                print(f" -> Table {table} is empty, skipping.")
                continue

            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in sqlite_cursor.fetchall()]
            col_count = len(columns)

            placeholders = ', '.join(['%s'] * col_count)
            col_names = ', '.join([f"`{c}`" for c in columns])
            insert_query = f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})"

            mysql_cursor.executemany(insert_query, rows)
            mysql_conn.commit()
            print(f" -> Successfully moved {len(rows)} rows.")

        except Exception as e:
            print(f" -> Error migrating {table}: {e}")

    print("\nMigration Finished! Check phpMyAdmin.")
    sqlite_conn.close()
    mysql_conn.close()


if __name__ == "__main__":
    migrate()