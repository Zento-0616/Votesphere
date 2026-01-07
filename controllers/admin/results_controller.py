from PyQt6.QtCore import QTimer
from models.admin.results_model import ResultsModel
from view.admin.results_view import ResultsDashboardView


class ResultsController:
    def __init__(self, db):
        self.model = ResultsModel(db)
        self.view = ResultsDashboardView()
        self.view.position_filter.currentTextChanged.connect(self.refresh_display)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_display)
        self.timer.start(5000)
        self.refresh_display()

    def refresh_display(self):
        if self.view.isHidden():
            return
        positions = self.model.get_available_positions()
        current = self.view.position_filter.currentText()
        self.view.position_filter.blockSignals(True)
        self.view.position_filter.clear()
        self.view.position_filter.addItem("Show All Positions")
        self.view.position_filter.addItems(positions)
        if current in positions or current == "Show All Positions":
            self.view.position_filter.setCurrentText(current)
        self.view.position_filter.blockSignals(False)

        filter_text = self.view.position_filter.currentText()
        data = self.model.get_standings(None if filter_text == "Show All Positions" else filter_text)

        while self.view.results_layout.count():
            item = self.view.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for pos, candidates in data.items():
            card = self.view.create_position_card(pos, candidates)
            self.view.results_layout.addWidget(card)