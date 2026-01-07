class AdminModel:
    def __init__(self, db):
        self.db = db
    def get_stats(self):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='voter'")
        voters = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE voted=1")
        votes = cursor.fetchone()[0]
        cursor.close()
        return voters, votes
    def get_leader_data(self):
        cursor = self.db.get_connection().cursor(buffered=True)
        cursor.execute("SELECT name, votes, position FROM candidates ORDER BY votes DESC LIMIT 10")
        data = cursor.fetchall(); cursor.close()
        return data
    def get_election_config(self):
        return {'name': self.db.get_config('election_name'), 'status': self.db.get_config('election_status'), 'target_time': self.db.get_config('election_target_time')}
    def stop_election(self):
        self.db.update_config('election_status', 'inactive')
        self.db.update_config('election_target_time', "")