class ResultsModel:
    def __init__(self, db):
        self.db = db

    def get_available_positions(self):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position ASC")
        data = [r[0] for r in cursor.fetchall()]
        cursor.close()
        return data

    def get_standings(self, position=None):
        cursor = self.db.get_connection().cursor(buffered=True)
        if position:
            cursor.execute("SELECT name, votes FROM candidates WHERE position = %s ORDER BY votes DESC", (position,))
            data = {position: cursor.fetchall()}
        else:
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            positions = [row[0] for row in cursor.fetchall()]
            data = {}
            for pos in positions:
                cursor.execute("SELECT name, votes FROM candidates WHERE position = %s ORDER BY votes DESC", (pos,))
                data[pos] = cursor.fetchall()
        cursor.close()
        return data