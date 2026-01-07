from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class ArchiveViewDialog(QDialog):
    def __init__(self, title, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title);
        self.setFixedSize(750, 550)
        self.setStyleSheet("QDialog { background-color: #1e272e; }")
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background: rgba(0,0,0,0.2); color: white; border-radius: 12px; } QHeaderView::section { background: #2f3640; color: #f1c40f; font-weight: bold; }")
        layout.addWidget(self.table)
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(
            "background: #485460; color: white; font-weight: bold; padding: 10px; border-radius: 8px;")
        layout.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignRight)


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self);
        layout.setContentsMargins(40, 40, 40, 40)

        cards_layout = QHBoxLayout();
        cards_layout.setSpacing(20)
        self.btn_voter_arch = self.create_button("Voter Archives", "#3498db")
        self.btn_cand_arch = self.create_button("Candidate Archives", "#3498db")

        self.status_lbl = QLabel("STATUS: OFFLINE ❌");
        self.status_lbl.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.ip_display = QLabel("Initializing...");
        self.ip_display.setStyleSheet("color: white; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 8px;")

        self.new_pass = QLineEdit(placeholderText="New Password", echoMode=QLineEdit.EchoMode.Password)
        self.confirm_pass = QLineEdit(placeholderText="Confirm Password", echoMode=QLineEdit.EchoMode.Password)
        self.btn_update_pass = self.create_button("UPDATE PASSWORD", "#27ae60")

        # Simple Card containers
        c1 = QFrame();
        cl1 = QVBoxLayout(c1);
        cl1.addWidget(QLabel("RECYCLE BIN"));
        cl1.addWidget(self.btn_voter_arch);
        cl1.addWidget(self.btn_cand_arch)
        c2 = QFrame();
        cl2 = QVBoxLayout(c2);
        cl2.addWidget(QLabel("VOTER PORTAL"));
        cl2.addWidget(self.status_lbl);
        cl2.addWidget(self.ip_display)
        c3 = QFrame();
        cl3 = QVBoxLayout(c3);
        cl3.addWidget(QLabel("SECURITY"));
        cl3.addWidget(self.new_pass);
        cl3.addWidget(self.confirm_pass);
        cl3.addWidget(self.btn_update_pass)

        for c in [c1, c2, c3]:
            c.setStyleSheet(
                "QFrame { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; } QLabel { color: white; font-weight: bold; }")
            cards_layout.addWidget(c)

        layout.addLayout(cards_layout);
        layout.addStretch()

    def create_button(self, text, color):
        btn = QPushButton(text);
        btn.setFixedHeight(45)
        btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: white; font-weight: bold; border-radius: 10px; border:none; }}")
        return btn