from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton
from models.admin.settings_model import SettingsModel
from view.admin.settings_view import SettingsView, ArchiveViewDialog

class SettingsController:
    def __init__(self, db):
        self.model = SettingsModel(db)
        self.view = SettingsView()
        self.view.btn_voter_arch.clicked.connect(lambda: self.open_archive("voters"))
        self.view.btn_cand_arch.clicked.connect(lambda: self.open_archive("candidates"))
        self.view.btn_update_pass.clicked.connect(self.handle_password_change)
        self.init_server()

    def init_server(self):
        try:
            from app import app
            if self.model.start_portal_server(app):
                ip = self.model.get_local_ip()
                self.view.status_lbl.setText("STATUS: ONLINE ✅")
                self.view.status_lbl.setStyleSheet("color: #2ecc71; font-weight: bold;")
                self.view.ip_display.setText(f"http://{ip}:5050")
        except: pass

    def handle_password_change(self):
        p1, p2 = self.view.new_pass.text(), self.view.confirm_pass.text()
        if p1 and p1 == p2:
            self.model.update_admin_password(p1)
            QMessageBox.information(self.view, "Success", "Password Updated.")
        else: QMessageBox.warning(self.view, "Error", "Passwords mismatch.")

    def open_archive(self, cat):
        cols = ["ID", "Name", "Grade", "Deleted At", "Action"] if cat == "voters" else ["Name", "Pos", "Deleted At", "Action"]
        dialog = ArchiveViewDialog(cat.title(), cols, self.view)
        data = self.model.get_archive_data(cat)
        dialog.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row): dialog.table.setItem(i, j, QTableWidgetItem(str(val)))
        dialog.close_btn.clicked.connect(dialog.close)
        dialog.exec()