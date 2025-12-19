from PyQt6.QtWidgets import QMessageBox, QFileDialog

class AdminController:
    def __init__(self, db_model):
        self.db = db_model

    def toggle_election(self, status, setup_data=None):
        if status == 'active' and setup_data:
            name, date, duration, target_time = setup_data
            self.db.update_config('election_name', name)
            self.db.update_config('election_target_time', target_time)
            self.db.update_config('election_status', 'active')
            self.db.log_audit("admin", "Started Election", "System")
        else:
            self.db.update_config('election_status', 'inactive')
            self.db.update_config('election_target_time', "")
            self.db.log_audit("admin", "Stopped Election", "System")

    def archive_entity(self, entity_type, entity_id):
        if entity_type == "voter":
            self.db.archive_voter(entity_id)
        else:
            self.db.archive_candidate(entity_id)