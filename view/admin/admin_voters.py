import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QInputDialog, QMessageBox, QDialog, QFormLayout, QLineEdit,
                             QAbstractItemView, QComboBox)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QFont, QBrush, QColor, QRegularExpressionValidator


class AddVoterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Voter")
        self.setFixedSize(450, 500)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #4ca1af
                );
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("➕ Register New Voter")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form Container
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Input Style
        input_style = """
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: rgba(255,255,255,0.2);
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.5);
            }
        """

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter Student ID")
        self.id_input.setStyleSheet(input_style)
        id_validator = QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        self.id_input.setValidator(id_validator)
        form_layout.addRow("Student ID:", self.id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Full Name")
        self.name_input.setStyleSheet(input_style)
        name_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]*"))
        self.name_input.setValidator(name_validator)
        self.name_input.textEdited.connect(lambda text: self.auto_capitalize(self.name_input, text))
        form_layout.addRow("Full Name:", self.name_input)

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("e.g. Grade 12")
        self.grade_input.setStyleSheet(input_style)
        form_layout.addRow("Grade/Year:", self.grade_input)

        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("e.g. Section A")
        self.section_input.setStyleSheet(input_style)
        self.section_input.textEdited.connect(lambda text: self.auto_capitalize(self.section_input, text))
        form_layout.addRow("Section:", self.section_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.save_btn = QPushButton("✅ Register Voter")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white; padding: 12px;
                border-radius: 8px; font-weight: bold; font-size: 14px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover { background: #2ecc71; margin-top: -2px; }
        """)
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(231, 76, 60, 0.8); color: white;
                padding: 12px; border-radius: 8px; font-weight: bold;
                font-size: 14px; border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover { background: #e74c3c; }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def auto_capitalize(self, line_edit, text):
        cursor_pos = line_edit.cursorPosition()
        line_edit.setText(text.title())
        line_edit.setCursorPosition(cursor_pos)

    def get_data(self):
        return (
            self.id_input.text().strip(),
            self.name_input.text().strip(),
            self.grade_input.text().strip(),
            self.section_input.text().strip()
        )


class EditVoterDialog(QDialog):
    def __init__(self, db, voter_data):
        super().__init__()
        self.db = db
        self.voter_data = voter_data
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Edit Voter")
        self.setFixedSize(400, 400)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #4ca1af
                );
            }
            QLabel { color: white; font-weight: bold; font-size: 14px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("✏️ Edit Voter Information")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        input_style = """
            QLineEdit {
                background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.3);
                border-radius: 5px; padding: 8px; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #3498db; }
        """

        self.username_input = QLineEdit()
        self.username_input.setText(str(self.voter_data[1]))
        self.username_input.setStyleSheet(input_style)
        id_validator = QRegularExpressionValidator(QRegularExpression("[0-9]*"))
        self.username_input.setValidator(id_validator)
        form_layout.addRow("Official ID:", self.username_input)

        self.full_name_input = QLineEdit()
        self.full_name_input.setText(str(self.voter_data[2]))
        self.full_name_input.setStyleSheet(input_style)
        name_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]*"))
        self.full_name_input.setValidator(name_validator)
        self.full_name_input.textEdited.connect(lambda text: self.auto_capitalize(self.full_name_input, text))
        form_layout.addRow("Full Name:", self.full_name_input)

        self.grade_input = QLineEdit()
        self.grade_input.setText(str(self.voter_data[3]))
        self.grade_input.setStyleSheet(input_style)
        form_layout.addRow("Grade:", self.grade_input)

        self.section_input = QLineEdit()
        self.section_input.setText(str(self.voter_data[4]))
        self.section_input.setStyleSheet(input_style)
        self.section_input.textEdited.connect(lambda text: self.auto_capitalize(self.section_input, text))
        form_layout.addRow("Section:", self.section_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet(self.get_btn_style("#27ae60", "#219955"))
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet(self.get_btn_style("#e74c3c", "#c0392b"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def auto_capitalize(self, line_edit, text):
        cursor_pos = line_edit.cursorPosition()
        line_edit.setText(text.title())
        line_edit.setCursorPosition(cursor_pos)

    def get_btn_style(self, color, hover_color):
        return f"""
            QPushButton {{
                background: {color}; color: white; padding: 10px 20px;
                border-radius: 6px; font-weight: bold; border: 2px solid rgba(255,255,255,0.3);
            }}
            QPushButton:hover {{ background: {hover_color}; }}
        """

    def save_changes(self):
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        grade = self.grade_input.text().strip()
        section = self.section_input.text().strip()

        if not username or not full_name:
            QMessageBox.warning(self, "Error", "Username and Full Name are required!")
            return

        cursor = None
        try:
            # --- MYSQL FIX: Buffered cursor and placeholder %s ---
            cursor = self.db.conn.cursor(buffered=True)
            cursor.execute("SELECT id FROM users WHERE username=%s AND id!=%s", (username, self.voter_data[0]))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Username already exists!")
                return

            cursor.execute("SELECT id FROM users WHERE UPPER(full_name)=UPPER(%s) AND id!=%s",
                           (full_name, self.voter_data[0]))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "A voter with this Full Name already exists!")
                return

            cursor.execute("""
                           UPDATE users
                           SET username=%s, password=%s, full_name=%s, grade=%s, section=%s
                           WHERE id = %s
                           """, (username, username, full_name, grade, section, self.voter_data[0]))

            self.db.conn.commit()
            self.db.log_audit("admin", "Edit", "Voters", f"Edited voter: {username}")
            QMessageBox.information(self, "Success", "Voter information updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update voter: {str(e)}")
        finally:
            if cursor: cursor.close()


class ManageVoters(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.update_filter_options()
        self.load_voters()

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("👤 Manage Voters")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 5px;")
        layout.addWidget(title)

        # Add Button
        top_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD VOTER")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white; padding: 12px 25px;
                border-radius: 8px; font-weight: bold; font-size: 14px;
                border: 2px solid rgba(255,255,255,0.3);
            }
            QPushButton:hover { background: #219955; }
        """)
        add_btn.clicked.connect(self.add_voter)
        top_layout.addWidget(add_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        # Filter Section
        filter_style = """
            QLineEdit, QComboBox {
                background: rgba(0, 0, 0, 0.15); color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px; padding: 5px 15px;
                font-size: 14px; font-weight: bold; height: 45px; 
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3498db; background: rgba(255, 255, 255, 0.2); }
            QComboBox QAbstractItemView { background-color: #34495e; color: white; selection-background-color: #3498db; border: 1px solid white; }
        """

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by Name or ID...")
        self.search_input.setStyleSheet(filter_style)
        self.search_input.textChanged.connect(self.load_voters)
        filter_layout.addWidget(self.search_input, 2)

        self.grade_filter = QComboBox()
        self.grade_filter.setStyleSheet(filter_style)
        self.grade_filter.addItem("All Grades")
        self.grade_filter.currentTextChanged.connect(self.load_voters)
        filter_layout.addWidget(self.grade_filter, 1)

        self.section_filter = QComboBox()
        self.section_filter.setStyleSheet(filter_style)
        self.section_filter.addItem("All Sections")
        self.section_filter.currentTextChanged.connect(self.load_voters)
        filter_layout.addWidget(self.section_filter, 1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Student ID", "Full Name", "Grade", "Section", "Voted", "Actions"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(60)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 180)

        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(0,0,0,0.15); border: 2px solid rgba(255,255,255,0.25);
                border-radius: 15px; gridline-color: rgba(255,255,255,0.25); color: white;
            }
            QHeaderView::section { background: rgba(0,0,0,0.1); color: white; padding: 10px; border: none; font-weight: bold; }
            QTableWidget::item { background: rgba(0,0,0,0.2); padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.15); color: white; }
            QTableWidget::item:selected { background: rgba(52, 152, 219, 0.35); color: white; }
        """)
        layout.addWidget(self.table)

        # Stats
        stats_layout = QHBoxLayout()
        self.total_voters_label = QLabel("Total Voters: 0")
        self.voted_count_label = QLabel("Voted: 0")
        self.pending_count_label = QLabel("Pending: 0")

        for lbl in [self.total_voters_label, self.voted_count_label, self.pending_count_label]:
            lbl.setStyleSheet(
                "color: white; font-weight: bold; font-size: 14px; background: rgba(255,255,255,0.15); padding: 10px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.3);")
            stats_layout.addWidget(lbl)

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

    def update_filter_options(self):
        cursor = None
        try:
            cursor = self.db.conn.cursor(buffered=True)
            cur_g = self.grade_filter.currentText()
            cur_s = self.section_filter.currentText()

            self.grade_filter.blockSignals(True)
            self.section_filter.blockSignals(True)

            self.grade_filter.clear()
            self.grade_filter.addItem("All Grades")
            cursor.execute("SELECT DISTINCT grade FROM users WHERE role='voter' ORDER BY grade ASC")
            for g in cursor.fetchall():
                if g[0]: self.grade_filter.addItem(str(g[0]))

            self.section_filter.clear()
            self.section_filter.addItem("All Sections")
            cursor.execute("SELECT DISTINCT section FROM users WHERE role='voter' ORDER BY section ASC")
            for s in cursor.fetchall():
                if s[0]: self.section_filter.addItem(str(s[0]))

            idx_g = self.grade_filter.findText(cur_g)
            self.grade_filter.setCurrentIndex(idx_g if idx_g >= 0 else 0)
            idx_s = self.section_filter.findText(cur_s)
            self.section_filter.setCurrentIndex(idx_s if idx_s >= 0 else 0)

            self.grade_filter.blockSignals(False)
            self.section_filter.blockSignals(False)
        except Exception as e:
            print(f"Error updating filters: {e}")
        finally:
            if cursor: cursor.close()

    def load_voters(self):
        cursor = None
        try:
            cursor = self.db.conn.cursor(buffered=True)
            query = "SELECT id, username, full_name, grade, section, voted FROM users WHERE role = 'voter'"
            params = []

            search_text = self.search_input.text().strip()
            if search_text:
                # --- MYSQL FIX: Placeholder %s ---
                query += " AND (full_name LIKE %s OR username LIKE %s)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])

            grade_sel = self.grade_filter.currentText()
            if grade_sel != "All Grades":
                query += " AND grade = %s"
                params.append(grade_sel)

            section_sel = self.section_filter.currentText()
            if section_sel != "All Sections":
                query += " AND section = %s"
                params.append(section_sel)

            query += " ORDER BY grade ASC, section ASC, full_name ASC"

            cursor.execute(query, tuple(params))
            voters = cursor.fetchall()
            self.table.setRowCount(len(voters))

            voted_count = 0
            for row, voter in enumerate(voters):
                vid, username, full_name, grade, section, voted = voter
                if voted: voted_count += 1

                self.table.setItem(row, 0, QTableWidgetItem(str(username)))
                self.table.setItem(row, 1, QTableWidgetItem(str(full_name)))
                self.table.setItem(row, 2, QTableWidgetItem(str(grade)))
                self.table.setItem(row, 3, QTableWidgetItem(str(section)))

                voted_item = QTableWidgetItem("✅ Yes" if voted else "❌ No")
                voted_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                voted_item.setForeground(QBrush(QColor("#2ecc71" if voted else "#e74c3c")))
                self.table.setItem(row, 4, voted_item)

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                actions_layout.setSpacing(15)

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(60, 30)
                edit_btn.setStyleSheet(self.get_action_btn_style("#3498db", "#2980b9"))
                edit_btn.clicked.connect(lambda checked, v_id=vid, v_data=voter: self.edit_voter(v_id, v_data))
                actions_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(60, 30)
                delete_btn.setStyleSheet(self.get_action_btn_style("#e74c3c", "#c0392b"))
                delete_btn.clicked.connect(lambda checked, v_id=vid: self.delete_voter(v_id))
                actions_layout.addWidget(delete_btn)

                self.table.setCellWidget(row, 5, actions_widget)

            self.total_voters_label.setText(f"Total Voters: {len(voters)}")
            self.voted_count_label.setText(f"Voted: {voted_count}")
            self.pending_count_label.setText(f"Pending: {len(voters) - voted_count}")
        except Exception as e:
            print(f"Error loading voters: {e}")
        finally:
            if cursor: cursor.close()

    def get_action_btn_style(self, color, hover):
        return f"""
            QPushButton {{
                background: {color}; color: white; padding: 6px 10px;
                border-radius: 4px; border: 1px solid rgba(255,255,255,0.3);
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """

    def add_voter(self):
        if self.db.get_config('election_status') == 'active':
            QMessageBox.warning(self, "Restricted", "⛔ Stop the election before adding voters.")
            return

        dialog = AddVoterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, full_name, grade, section = dialog.get_data()
            if not username or not full_name:
                QMessageBox.warning(self, "Error", "ID and Name are required!")
                return

            cursor = None
            try:
                cursor = self.db.conn.cursor(buffered=True)
                cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "ID already exists!")
                    return

                cursor.execute("SELECT id FROM users WHERE UPPER(full_name)=UPPER(%s)", (full_name,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Error", "Name already exists!")
                    return

                cursor.execute("""
                    INSERT INTO users (username, password, role, full_name, grade, section)
                    VALUES (%s, %s, 'voter', %s, %s, %s)
                """, (username, username, full_name, grade, section))
                self.db.conn.commit()
                self.update_filter_options()
                self.load_voters()
                self.db.log_audit("admin", "Add", "Voters", f"Registered: {username}")
                QMessageBox.information(self, "Success", "Voter added!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                if cursor: cursor.close()

    def edit_voter(self, voter_id, voter_data):
        if self.db.get_config('election_status') == 'active':
            QMessageBox.warning(self, "Restricted", "⛔ Stop the election first.")
            return
        dialog = EditVoterDialog(self.db, voter_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_filter_options()
            self.load_voters()

    def delete_voter(self, voter_id):
        if self.db.get_config('election_status') == 'active':
            QMessageBox.warning(self, "Restricted", "⛔ Stop the election first.")
            return
        if QMessageBox.question(self, "Delete", "Move to Recycle Bin?") == QMessageBox.StandardButton.Yes:
            try:
                self.db.archive_voter(voter_id)
                self.update_filter_options()
                self.load_voters()
                self.db.log_audit("admin", f"Archived voter ID: {voter_id}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))