from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CustomPopup(QDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(380, 220)

        self.setStyleSheet("""
            QDialog {
                background: #1a252f;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)

        layout = QVBoxLayout(self)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("color: #3498db;")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    @staticmethod
    def show_error(parent, title, message):
        popup = CustomPopup(parent, title, message)
        popup.exec()

    @staticmethod
    def show_message(parent, title, message):
        popup = CustomPopup(parent, title, message)
        popup.exec()
