from mysql.connector import Error

class VoterModel:
    def __init__(self, db):
        self.db = db

    def get_user_name(self, user_id):
        cursor = self.db.get_connection().cursor()
        cursor.execute("SELECT full_name FROM users WHERE id=%s", (user_id,))
        res = cursor.fetchone()
        cursor.close()
        return res[0] if res else "Student"

    def check_voted(self, user_id):
        return self.db.check_user_voted(user_id)

    def get_election_status(self):
        return self.db.get_config('election_status')

    def get_target_time(self):
        return self.db.get_config('election_target_time')

    def get_positions(self):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
        res = [r[0] for r in cursor.fetchall()]
        cursor.close()
        return res

    def get_candidates(self, position):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT id, name, grade, image FROM candidates WHERE position=%s", (position,))
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_trends(self):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
        positions = [r[0] for r in cursor.fetchall()]
        trends = {}
        for pos in positions:
            cursor.execute("SELECT name, votes FROM candidates WHERE position=%s ORDER BY votes DESC LIMIT 3", (pos,))
            trends[pos] = cursor.fetchall()
        cursor.close()
        return trends

    def update_heartbeat(self, user_id, session_token):
        conn = self.db.get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT session_token FROM users WHERE id=%s", (user_id,))
        res = cursor.fetchone()
        if not res or res[0] != session_token:
            cursor.close()
            return False
        cursor.execute("UPDATE users SET last_active=NOW() WHERE id=%s", (user_id,))
        self.db.conn.commit()
        cursor.close()
        return True

    def submit_ballot(self, user_id, user_name, selections):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            receipt = []
            for pos, cand_id in selections.items():
                cursor.execute("INSERT INTO votes (voter_id, candidate_id, position) VALUES (%s, %s, %s)", (user_id, cand_id, pos))
                cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id=%s", (cand_id,))
                cursor.execute("SELECT name FROM candidates WHERE id=%s", (cand_id,))
                n = cursor.fetchone()[0]
                receipt.append((pos, n))
            cursor.execute("UPDATE users SET voted=1 WHERE id=%s", (user_id,))
            self.db.log_audit(user_name, "Ballot Finalized")
            conn.commit()
            return True, receipt
        except Exception:
            conn.rollback()
            return False, []
        finally:
            cursor.close()

    def clear_session(self, user_id):
        cursor = self.db.get_connection().cursor()
        cursor.execute("UPDATE users SET last_active = NULL WHERE id=%s", (user_id,))
        self.db.conn.commit()
        cursor.close()