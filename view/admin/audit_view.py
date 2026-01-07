from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class AuditLogView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("🛡️ Security Audit Logs")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.live_indicator = QLabel("● LIVE")
        self.live_indicator.setStyleSheet("color: #2ecc71; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.live_indicator)
        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "User", "Module", "Action", "Description"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
           QTableWidget {
                background: rgba(0,0,0,0.25); 
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
            }
            QHeaderView::section {
                background: #1a252f; 
                color: #f1c40f;
                padding: 10px;
                border-bottom: 2px solid #2ecc71;
                font-weight: bold;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 140)
        layout.addWidget(self.table)

    def set_live_style(self, visible):
        if visible:
            self.live_indicator.setStyleSheet("color: #2ecc71; font-size: 18px; font-weight: bold;")
        else:
            self.live_indicator.setStyleSheet("color: rgba(46, 204, 113, 0.2); font-size: 18px; font-weight: bold;")