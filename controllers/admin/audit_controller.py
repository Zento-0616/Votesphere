from PyQt6.QtCore import QObject, QTimer, Qt
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QColor, QFont
from models.admin.audit_model import AuditModel
from view.admin.audit_view import AuditLogView


class AuditLogController(QObject):
    def __init__(self, db):
        super().__init__()
        self.model = AuditModel(db)
        self.view = AuditLogView()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_logs)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.handle_blink)
        self.blink_state = True

        self.update_logs()
        self.refresh_timer.start(3000)
        self.blink_timer.start(800)

    def handle_blink(self):
        self.blink_state = not self.blink_state
        self.view.set_live_style(self.blink_state)

    def update_logs(self):
        scrollbar = self.view.table.verticalScrollBar()
        current_pos = scrollbar.value()

        logs = self.model.fetch_logs()
        if len(logs) == self.view.table.rowCount() and len(logs) > 0:
            return

        self.view.table.setUpdatesEnabled(False)
        self.view.table.setRowCount(len(logs))

        for row_idx, log in enumerate(logs):
            items = [
                QTableWidgetItem(log["time"]),
                QTableWidgetItem(log["user"]),
                QTableWidgetItem(log["module"]),
                QTableWidgetItem(log["action"]),
                QTableWidgetItem(log["description"])
            ]
            color = self.model.get_module_color(log["module"])
            items[2].setForeground(QColor(color))
            items[2].setFont(QFont("Arial", 10, QFont.Weight.Bold))

            for col_idx, item in enumerate(items):
                if col_idx < 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.view.table.setItem(row_idx, col_idx, item)

        self.view.table.setUpdatesEnabled(True)
        scrollbar.setValue(current_pos)