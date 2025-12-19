from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QInputDialog, QMessageBox, QAbstractItemView, QDialog,
                             QFormLayout, QLineEdit, QComboBox, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression


class AddCandidateDialog(QDialog):
    def __init__(self, parent=None, candidate_data=None):
        super().__init__(parent)
        self.candidate_data = candidate_data

        if self.candidate_data:
            self.setWindowTitle("Edit Candidate")
        else:
            self.setWindowTitle("Add New Candidate")

        self.setFixedSize(450, 550)
        self.image_data = None

        if self.candidate_data and len(self.candidate_data) > 5:
            self.image_data = self.candidate_data[5]

        self.setup_ui()

        if self.candidate_data:
            self.load_existing_data()

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
        title_text = "Edit Candidate" if self.candidate_data else "➕ New Candidate"
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        img_layout = QVBoxLayout()
        self.image_preview = QLabel("No Image Selected")
        self.image_preview.setFixedSize(100, 100)
        self.image_preview.setStyleSheet("border: 2px dashed rgba(255,255,255,0.5); border-radius: 50px;")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        upload_btn = QPushButton("📷 Upload Photo")
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setStyleSheet("""
            QPushButton {
                background: #3498db; color: white; padding: 8px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background: #2980b9; }
        """)
        upload_btn.clicked.connect(self.select_image)

        img_container = QHBoxLayout()
        img_container.addStretch()
        img_container.addWidget(self.image_preview)
        img_container.addStretch()

        img_layout.addLayout(img_container)
        img_layout.addWidget(upload_btn)
        layout.addLayout(img_layout)

        # Form Container
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        input_style = """
            QLineEdit {
                background: rgba(0,0,0,0.4); 
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: rgba(0,0,0,0.6);
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.5);
            }
        """

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Candidate Name")
        self.name_input.setStyleSheet(input_style)

        name_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]*"))
        self.name_input.setValidator(name_validator)
        self.name_input.textEdited.connect(lambda text: self.auto_capitalize(self.name_input, text))

        form_layout.addRow("Full Name:", self.name_input)

        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("e.g. President")
        self.position_input.setStyleSheet(input_style)

        pos_validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]*"))
        self.position_input.setValidator(pos_validator)
        self.position_input.textEdited.connect(lambda text: self.auto_uppercase(self.position_input, text))

        form_layout.addRow("Position:", self.position_input)

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("e.g. Grade 12")
        self.grade_input.setStyleSheet(input_style)
        form_layout.addRow("Grade/Year:", self.grade_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_text = "💾 Update" if self.candidate_data else "✅ Save Candidate"
        self.save_btn = QPushButton(btn_text)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover {
                background: #2ecc71;
                margin-top: -2px;
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(231, 76, 60, 0.8);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover {
                background: #e74c3c;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def auto_capitalize(self, line_edit, text):
        cursor_pos = line_edit.cursorPosition()
        line_edit.setText(text.title())
        line_edit.setCursorPosition(cursor_pos)

    def auto_uppercase(self, line_edit, text):
        cursor_pos = line_edit.cursorPosition()
        line_edit.setText(text.upper())
        line_edit.setCursorPosition(cursor_pos)

    def load_existing_data(self):
        try:
            self.name_input.setText(self.candidate_data[1])
            self.position_input.setText(self.candidate_data[2])
            self.grade_input.setText(self.candidate_data[3])

            if self.image_data:
                pixmap = QPixmap()
                pixmap.loadFromData(self.image_data)
                self.image_preview.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                           Qt.TransformationMode.SmoothTransformation))
                self.image_preview.setStyleSheet("border: 2px solid white; border-radius: 50px;")
                self.image_preview.setText("")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.image_preview.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                       Qt.TransformationMode.SmoothTransformation))
            self.image_preview.setStyleSheet("border: 2px solid white; border-radius: 50px;")
            self.image_preview.setText("")

            with open(file_name, 'rb') as f:
                self.image_data = f.read()

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.position_input.text().strip(),
            self.grade_input.text().strip(),
            self.image_data
        )


class ManageCandidates(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.update_filter_options()
        self.load_candidates()

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("👥 Manage Candidates")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # Top Row
        top_layout = QHBoxLayout()
        add_btn = QPushButton("➕ ADD CANDIDATE")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255,255,255,0.3);
            }
            QPushButton:hover {
                background: #219955;
            }
        """)
        add_btn.clicked.connect(self.add_candidate)
        top_layout.addWidget(add_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Filter Section
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        filter_style = """
            QLineEdit, QComboBox {
                background: rgba(0, 0, 0, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 14px;
                font-weight: bold;
                height: 45px; 
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
                background: rgba(255, 255, 255, 0.2);
            }
            QComboBox::drop-down {
                border: 0px;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: white;
                selection-background-color: #3498db;
                border: 1px solid white;
            }
        """

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Candidate Name...")
        self.search_input.setStyleSheet(filter_style)
        self.search_input.textChanged.connect(self.load_candidates)
        filter_layout.addWidget(self.search_input, 2)

        # Position Filter
        self.position_filter = QComboBox()
        self.position_filter.setStyleSheet(filter_style)
        self.position_filter.addItem("All Positions")
        self.position_filter.currentTextChanged.connect(self.load_candidates)
        filter_layout.addWidget(self.position_filter, 1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Position", "Grade", "Actions"])

        # TABLE READ ONLY
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.table.verticalHeader().setDefaultSectionSize(60)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 230)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 120)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 180)

        self.table.horizontalHeader().setMinimumSectionSize(100)

        self.table.setStyleSheet("""
           QTableWidget {
                background: rgba(0,0,0,0.15); 
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 25px;
                gridline-color: rgba(255,255,255,0.2);
                color: white;
                font-size: 14px;
            }
            QHeaderView::section {
                background: rgba(0,0,0,0.1); 
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
            QTableWidget::item {
                background: rgba(0,0,0,0.2);
                padding: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.15);
            }
            QTableWidget::item:selected {
                background: rgba(52, 152, 219, 0.35);
                color: white;
            }
        """)
        layout.addWidget(self.table)

    def update_filter_options(self):
        try:
            cursor = self.db.conn.cursor()

            current_pos = self.position_filter.currentText()

            self.position_filter.blockSignals(True)
            self.position_filter.clear()
            self.position_filter.addItem("All Positions")

            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position ASC")
            positions = cursor.fetchall()
            for p in positions:
                if p[0]: self.position_filter.addItem(p[0])

            index = self.position_filter.findText(current_pos)
            if index >= 0:
                self.position_filter.setCurrentIndex(index)

            self.position_filter.blockSignals(False)
        except Exception as e:
            print(f"Error updating filters: {e}")

    def load_candidates(self):
        try:
            cursor = self.db.conn.cursor()

            query = "SELECT id, name, position, grade FROM candidates WHERE 1=1"
            params = []

            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND name LIKE ?"
                params.append(f"%{search_text}%")

            pos_sel = self.position_filter.currentText()
            if pos_sel != "All Positions":
                query += " AND position = ?"
                params.append(pos_sel)

            query += " ORDER BY LENGTH(grade) ASC, grade ASC, position ASC, name ASC"

            cursor.execute(query, tuple(params))
            candidates = cursor.fetchall()

            self.table.setRowCount(len(candidates))

            for row, candidate in enumerate(candidates):
                id, name, position, grade = candidate

                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(position))
                self.table.setItem(row, 2, QTableWidgetItem(grade))

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(15)
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedSize(60, 30)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background: #3498db;
                        color: white;
                        padding: 6px 10px;
                        border-radius: 5px;
                        border: 1px solid rgba(255,255,255,0.3);
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, cid=id: self.edit_candidate(cid))
                actions_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(60, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background: #e74c3c;
                        color: white;
                        padding: 6px 10px;
                        border-radius: 5px;
                        border: 1px solid rgba(255,255,255,0.3);
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, cid=id: self.delete_candidate(cid))
                actions_layout.addWidget(delete_btn)

                self.table.setCellWidget(row, 3, actions_widget)
        except Exception as e:
            print(f"Error loading candidates: {e}")

    def add_candidate(self):
        status = self.db.get_config('election_status')
        if status == 'active':
            QMessageBox.warning(self, "Action Restricted",
                                "⛔ Cannot add candidates while Election is LIVE.\nPlease stop the election first.")
            return

        dialog = AddCandidateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, position, grade, image_data = dialog.get_data()

            if name and position and grade:
                try:
                    cursor = self.db.conn.cursor()

                    cursor.execute("SELECT id FROM candidates WHERE UPPER(name)=UPPER(?)", (name,))
                    if cursor.fetchone():
                        QMessageBox.warning(self, "Duplicate Candidate",
                                            f"A candidate named '{name}' already exists (Case Insensitive)!")
                        return

                    # Insert with image blob
                    cursor.execute("INSERT INTO candidates (name, position, grade, image) VALUES (?, ?, ?, ?)",
                                   (name, position, grade, image_data))
                    self.db.conn.commit()

                    self.update_filter_options()
                    self.load_candidates()
                    self.db.log_audit("admin", "Add", "Candidates", f"Added candidate: {name} for {position}")
                    QMessageBox.information(self, "Success", "Candidate added successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add candidate: {str(e)}")
            else:
                QMessageBox.warning(self, "Missing Input", "All text fields are required!")

    def edit_candidate(self, candidate_id):
        status = self.db.get_config('election_status')
        if status == 'active':
            QMessageBox.warning(self, "Action Restricted",
                                "⛔ Cannot edit candidates while Election is LIVE.\nPlease stop the election first.")
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT id, name, position, grade, votes, image FROM candidates WHERE id=?", (candidate_id,))
            candidate_data = cursor.fetchone()

            if not candidate_data:
                QMessageBox.warning(self, "Error", "Candidate not found!")
                return

            dialog = AddCandidateDialog(self, candidate_data=candidate_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                name, position, grade, image_data = dialog.get_data()

                if name and position and grade:
                    if name.upper() != candidate_data[1].upper():
                        cursor.execute("SELECT id FROM candidates WHERE UPPER(name)=UPPER(?) AND id!=?",
                                       (name, candidate_id))
                        if cursor.fetchone():
                            QMessageBox.warning(self, "Duplicate Candidate",
                                                f"A candidate named '{name}' already exists!")
                            return

                    cursor.execute("""
                        UPDATE candidates 
                        SET name=?, position=?, grade=?, image=? 
                        WHERE id=?
                    """, (name, position, grade, image_data, candidate_id))

                    self.db.conn.commit()
                    self.update_filter_options()
                    self.load_candidates()
                    self.db.log_audit("admin", "Edit", "Candidates", f"Edited candidate: {name} for {position}")
                    QMessageBox.information(self, "Success", "Candidate updated successfully!")
                else:
                    QMessageBox.warning(self, "Missing Input", "All fields are required!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit candidate: {str(e)}")

    def delete_candidate(self, candidate_id):
        status = self.db.get_config('election_status')
        if status == 'active':
            QMessageBox.warning(self, "Action Restricted",
                                "⛔ Cannot delete candidates while Election is LIVE.\nPlease stop the election first.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this candidate?\n(It will be moved to the Archive/Recycle Bin)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.archive_candidate(candidate_id)

                self.update_filter_options()
                self.load_candidates()
                self.db.log_audit("admin", "Delete", "Candidates", f"Archived candidate ID: {candidate_id}")
                QMessageBox.information(self, "Success", "Candidate moved to Archive/Recycle Bin!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete candidate: {str(e)}")