from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QFormLayout, QLineEdit,
                             QMessageBox, QDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QTabWidget, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# RECYCLE BIN DIALOG
class DeletedItemsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("🗑️ Recycle Bin (Retained for 30 Days)")
        self.setFixedSize(750, 550)
        self.setStyleSheet("background: #2c3e50; color: white;")

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #7f8c8d; }
            QTabBar::tab { background: #34495e; color: white; padding: 10px; }
            QTabBar::tab:selected { background: #3498db; }
        """)

        # VOTERS TAB
        voter_widget = QWidget()
        v_layout = QVBoxLayout(voter_widget)
        self.voters_table = self.create_table(["Username", "Name", "Grade", "Section", "Deleted Date"])
        v_layout.addWidget(self.voters_table)

        restore_v_btn = QPushButton("♻️ Restore Selected Voter")
        restore_v_btn.setStyleSheet(self.get_btn_style("#27ae60"))
        restore_v_btn.clicked.connect(self.restore_selected_voter)
        v_layout.addWidget(restore_v_btn)

        self.tabs.addTab(voter_widget, "Deleted Voters")

        # CANDIDATES TAB
        cand_widget = QWidget()
        c_layout = QVBoxLayout(cand_widget)
        self.candidates_table = self.create_table(["Name", "Position", "Grade", "Deleted Date"])
        c_layout.addWidget(self.candidates_table)

        restore_c_btn = QPushButton("♻️ Restore Selected Candidate")
        restore_c_btn.setStyleSheet(self.get_btn_style("#27ae60"))
        restore_c_btn.clicked.connect(self.restore_selected_candidate)
        c_layout.addWidget(restore_c_btn)

        self.tabs.addTab(cand_widget, "Deleted Candidates")

        layout.addWidget(self.tabs)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("background: #e74c3c; padding: 8px; border-radius: 4px; font-weight: bold;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.load_data()

    def get_btn_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.3);
            }}
            QPushButton:hover {{ background-color: white; color: {color}; }}
        """

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setStyleSheet("background: rgba(0,0,0,0.2); border: none; gridline-color: #555;")
        return table

    def load_data(self):
        self.voters_table.setRowCount(0)
        voters = self.db.get_archives("voters")
        self.voters_table.setRowCount(len(voters))
        for r, row_data in enumerate(voters):
            for c, item in enumerate(row_data):
                self.voters_table.setItem(r, c, QTableWidgetItem(str(item)))

        self.candidates_table.setRowCount(0)
        candidates = self.db.get_archives("candidates")
        self.candidates_table.setRowCount(len(candidates))
        for r, row_data in enumerate(candidates):
            for c, item in enumerate(row_data):
                self.candidates_table.setItem(r, c, QTableWidgetItem(str(item)))

    def restore_selected_voter(self):
        row = self.voters_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a voter to restore.")
            return

        username = self.voters_table.item(row, 0).text()
        try:
            self.db.restore_voter(username)
            self.db.log_audit("admin", "Restore", "Voters", f"Restored voter: {username}")
            QMessageBox.information(self, "Success",
                                    f"Voter '{username}' has been restored.\nPassword is now their username.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore: {e}")

    def restore_selected_candidate(self):
        row = self.candidates_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a candidate to restore.")
            return

        name = self.candidates_table.item(row, 0).text()
        try:
            self.db.restore_candidate(name)
            self.db.log_audit("admin", "Restore", "Candidates", f"Restored candidate: {name}")
            QMessageBox.information(self, "Success", f"Candidate '{name}' has been restored.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore: {e}")


class SettingsWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("⚙️ System Settings")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # ADMIN SECURITY
        security_box = QGroupBox("Admin Security")
        security_box.setStyleSheet(self.get_groupbox_style())
        sec_layout = QFormLayout(security_box)
        sec_layout.setVerticalSpacing(15)

        self.current_pass_input = QLineEdit()
        self.current_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pass_input.setPlaceholderText("Current Password")
        self.current_pass_input.setStyleSheet(self.get_input_style())
        sec_layout.addRow("Current Password:", self.current_pass_input)

        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setPlaceholderText("New Password")
        self.new_pass_input.setStyleSheet(self.get_input_style())
        sec_layout.addRow("New Password:", self.new_pass_input)

        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setPlaceholderText("Confirm New Password")
        self.confirm_pass_input.setStyleSheet(self.get_input_style())
        sec_layout.addRow("Confirm Password:", self.confirm_pass_input)

        change_pass_btn = QPushButton("Update Password")
        change_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pass_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22; color: white; padding: 10px;
                border-radius: 5px; font-weight: bold; font-size: 14px;
                border: 1px solid rgba(255,255,255,0.3);
            }
            QPushButton:hover { background: #d35400; }
        """)
        change_pass_btn.clicked.connect(self.change_admin_password)
        sec_layout.addRow("", change_pass_btn)
        layout.addWidget(security_box)

        # DATA MANAGEMENT
        archive_box = QGroupBox("Data Management")
        archive_box.setStyleSheet(self.get_groupbox_style())
        archive_layout = QVBoxLayout(archive_box)
        archive_layout.setContentsMargins(10, 15, 10, 10)
        archive_layout.setSpacing(10)

        # View Recycle Bin
        self.view_bin_btn = QPushButton("🗑️ View Deleted Records (Recycle Bin)")
        self.view_bin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_bin_btn.setStyleSheet("""
            QPushButton {
                background: #7f8c8d; color: white; padding: 10px;
                border-radius: 5px; font-weight: bold; font-size: 14px;
                border: 1px solid rgba(255,255,255,0.3);
            }
            QPushButton:hover { background: #95a5a6; }
        """)
        self.view_bin_btn.clicked.connect(self.open_recycle_bin)
        archive_layout.addWidget(self.view_bin_btn)

        layout.addWidget(archive_box)
        layout.addStretch()

    # HELPER METHODS
    def get_groupbox_style(self):
        return "QGroupBox { color: white; font-weight: bold; font-size: 16px; background: rgba(0,0,0,0.15); border: 2px solid rgba(255,255,255,0.3); border-radius: 10px; margin-top: 20px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 5px 10px; background: #c0392b; border-radius: 5px; }"

    def get_input_style(self):
        return "QLineEdit { background: #c2c2c2; border: 1px solid rgba(0,0,0,0.2); border-radius: 5px; padding: 5px; font-size: 16px; font-weight: bold; color: #2c3e50; min-height: 30px; }"

    def open_recycle_bin(self):
        dialog = DeletedItemsDialog(self.db, self)
        dialog.exec()

    def change_admin_password(self):
        current = self.current_pass_input.text().strip()
        new = self.new_pass_input.text().strip()
        confirm = self.confirm_pass_input.text().strip()

        if not current or not new or not confirm: return QMessageBox.warning(self, "Error", "All fields required.")
        if new != confirm: return QMessageBox.warning(self, "Error", "Passwords do not match.")

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username='admin'")
            res = cursor.fetchone()
            if res and res[0] == current:
                cursor.execute("UPDATE users SET password=? WHERE username='admin'", (new,))
                self.db.conn.commit()
                self.db.log_audit("admin", "Changed password")
                QMessageBox.information(self, "Success", "Password updated!")
                self.current_pass_input.clear();
                self.new_pass_input.clear();
                self.confirm_pass_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Incorrect current password.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))