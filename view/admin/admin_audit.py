from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer


class AuditLogViewer(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_logs)
        self.timer.setInterval(3000)

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🛡️ Security Audit Logs")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)

        header_layout.addStretch()


        self.live_indicator = QLabel("● LIVE")
        self.live_indicator.setStyleSheet("color: #2ecc71; font-size: 40px; font-weight: bold; margin-right: 10px;")
        header_layout.addWidget(self.live_indicator)


        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "User", "Module", "Action", "Description"])

        # Read-only
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.verticalHeader().setVisible(False)

        # Styling
        self.table.setStyleSheet("""
           QTableWidget {
                background: rgba(0,0,0,0.15); 
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 15px;
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
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            QTableWidget::item:selected {
                background: rgba(52, 152, 219, 0.35);
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        # Time
        self.table.setColumnWidth(0, 180)
        # User
        self.table.setColumnWidth(1, 150)
        # Module
        self.table.setColumnWidth(2, 100)
        # Action
        self.table.setColumnWidth(3, 150)

        layout.addWidget(self.table)


    def showEvent(self, event):
        self.load_logs()
        self.timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def load_logs(self):
        current_scroll_pos = self.table.verticalScrollBar().value()

        # Stop Updates
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        self.table.clearContents()

        # Fetch Data
        logs = self.db.get_audit_logs()
        self.table.setRowCount(len(logs))

        # Populate Data
        for row_idx, log_data in enumerate(logs):
            safe_data = log_data if len(log_data) == 5 else (*log_data, "", "", "", "")[:5]

            for col_idx, data in enumerate(safe_data):
                item = QTableWidgetItem(str(data))

                if col_idx == 2:
                    if data == "Security":
                        item.setForeground(QColor("#e74c3c"))
                    elif data == "Election":
                        item.setForeground(QColor("#f1c40f"))
                    elif data == "Voters":
                        item.setForeground(QColor("#3498db"))
                    elif data == "Candidates":
                        item.setForeground(QColor("#2ecc71"))
                    else:
                        item.setForeground(QColor("white"))

                self.table.setItem(row_idx, col_idx, item)


        self.table.setUpdatesEnabled(True)
        if self.table.rowCount() > 0:
            self.table.verticalScrollBar().setValue(current_scroll_pos)