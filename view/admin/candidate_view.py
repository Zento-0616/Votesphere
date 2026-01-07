from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QDialog, QFormLayout, QLineEdit,
                             QComboBox, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression


class AddCandidateDialog(QDialog):
    def __init__(self, parent=None, candidate_data=None):
        super().__init__(parent)
        self.candidate_data = candidate_data
        self.image_data = candidate_data[5] if candidate_data and len(candidate_data) > 5 else None
        self.setWindowTitle("Edit Candidate" if candidate_data else "Add New Candidate")
        self.setFixedSize(450, 550)
        self.setup_ui()
        if self.candidate_data:
            self.load_data()

    def setup_ui(self):
        self.setStyleSheet(
            "QDialog { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #4ca1af); } QLabel { color: white; font-weight: bold; font-size: 14px; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Edit Candidate" if self.candidate_data else "➕ New Candidate")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        layout.addWidget(title)

        self.image_preview = QLabel("No Image Selected")
        self.image_preview.setFixedSize(100, 100)
        self.image_preview.setStyleSheet("border: 2px dashed rgba(255,255,255,0.5); border-radius: 50px;")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        upload_btn = QPushButton("📷 Upload Photo")
        upload_btn.setStyleSheet(
            "QPushButton { background: #3498db; color: white; padding: 8px; border-radius: 5px; font-weight: bold; }")
        upload_btn.clicked.connect(self.select_image)

        img_container = QHBoxLayout()
        img_container.addStretch()
        img_container.addWidget(self.image_preview)
        img_container.addStretch()
        layout.addLayout(img_container)
        layout.addWidget(upload_btn)

        form_layout = QFormLayout()
        input_style = "QLineEdit { background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; padding: 10px; color: white; }"

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        self.name_input.setValidator(QRegularExpressionValidator(QRegularExpression("[a-zA-Z ]*")))
        self.name_input.textEdited.connect(lambda t: self.name_input.setText(t.title()))

        self.position_input = QLineEdit()
        self.position_input.setStyleSheet(input_style)
        self.position_input.textEdited.connect(lambda t: self.position_input.setText(t.upper()))

        self.grade_input = QLineEdit()
        self.grade_input.setStyleSheet(input_style)

        form_layout.addRow("Full Name:", self.name_input)
        form_layout.addRow("Position:", self.position_input)
        form_layout.addRow("Grade/Year:", self.grade_input)
        layout.addLayout(form_layout)

        btns = QHBoxLayout()
        self.save_btn = QPushButton("💾 Update" if self.candidate_data else "✅ Save")
        self.save_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: white; padding: 12px; border-radius: 8px; font-weight: bold; }")
        self.save_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet(
            "QPushButton { background: #e74c3c; color: white; padding: 12px; border-radius: 8px; font-weight: bold; }")
        self.cancel_btn.clicked.connect(self.reject)

        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            pix = QPixmap(path)
            self.image_preview.setPixmap(pix.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                    Qt.TransformationMode.SmoothTransformation))
            self.image_preview.setText("")
            with open(path, 'rb') as f: self.image_data = f.read()

    def load_data(self):
        self.name_input.setText(self.candidate_data[1])
        self.position_input.setText(self.candidate_data[2])
        self.grade_input.setText(self.candidate_data[3])
        if self.image_data:
            pix = QPixmap()
            pix.loadFromData(self.image_data)
            self.image_preview.setPixmap(pix.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
            self.image_preview.setText("")

    def get_values(self):
        return self.name_input.text().strip(), self.position_input.text().strip(), self.grade_input.text().strip(), self.image_data


class ManageCandidatesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QHBoxLayout()
        title = QLabel("👥 Manage Candidates")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        self.add_btn = QPushButton("➕ ADD CANDIDATE")
        self.add_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: white; padding: 12px 25px; border-radius: 8px; font-weight: bold; }")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        filter_row = QHBoxLayout()
        style = "QLineEdit, QComboBox { background: rgba(0,0,0,0.15); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; padding: 10px; }"

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Name...")
        self.search_input.setStyleSheet(style)

        self.pos_filter = QComboBox()
        self.pos_filter.setStyleSheet(style)
        self.pos_filter.addItem("All Positions")

        filter_row.addWidget(self.search_input, 2)
        filter_row.addWidget(self.pos_filter, 1)
        layout.addLayout(filter_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Position", "Grade", "Actions"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background: rgba(0,0,0,0.15); color: white; border-radius: 15px; } QHeaderView::section { background: rgba(0,0,0,0.3); color: white; font-weight: bold; }")
        layout.addWidget(self.table)