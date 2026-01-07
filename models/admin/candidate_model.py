import mysql.connector

class CandidateModel:
    def __init__(self, db):
        self.db = db

    def get_election_status(self):
        return self.db.get_config('election_status')

    def fetch_positions(self):
        cursor = self.db.conn.cursor(buffered=True)
        cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position ASC")
        positions = [p[0] for p in cursor.fetchall() if p[0]]
        cursor.close()
        return positions

    def fetch_candidates(self, search_text="", position_filter="All Positions"):
        cursor = self.db.conn.cursor(buffered=True)
        query = "SELECT id, name, position, grade FROM candidates WHERE 1=1"
        params = []

        if search_text:
            query += " AND name LIKE %s"
            params.append(f"%{search_text}%")

        if position_filter != "All Positions":
            query += " AND position = %s"
            params.append(position_filter)

        query += " ORDER BY LENGTH(grade) ASC, grade ASC, position ASC, name ASC"
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_candidate_details(self, candidate_id):
        cursor = self.db.conn.cursor(buffered=True)
        cursor.execute("SELECT id, name, position, grade, votes, image FROM candidates WHERE id=%s", (candidate_id,))
        data = cursor.fetchone()
        cursor.close()
        return data

    def is_duplicate(self, name, exclude_id=None):
        cursor = self.db.conn.cursor(buffered=True)
        if exclude_id:
            cursor.execute("SELECT id FROM candidates WHERE UPPER(name)=UPPER(%s) AND id!=%s", (name, exclude_id))
        else:
            cursor.execute("SELECT id FROM candidates WHERE UPPER(name)=UPPER(%s)", (name,))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

    def add_candidate(self, name, position, grade, image):
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO candidates (name, position, grade, image) VALUES (%s, %s, %s, %s)",
                       (name, position, grade, image))
        self.db.conn.commit()
        cursor.close()

    def update_candidate(self, cid, name, position, grade, image):
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE candidates SET name=%s, position=%s, grade=%s, image=%s WHERE id=%s",
                       (name, position, grade, image, cid))
        self.db.conn.commit()
        cursor.close()

    def delete_candidate(self, cid):
        self.db.archive_candidate(cid)

    def log_action(self, action, description):
        self.db.log_audit("admin", action, "Candidates", description)