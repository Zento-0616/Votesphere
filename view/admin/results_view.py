from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea, QFrame, QComboBox, QAbstractItemView, QSizePolicy, QDialog, QRadioButton,
                             QPushButton)
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtCore import Qt


class ExportResultsView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Election Results")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background-color: #1a252f; border: 2px solid #3498db; border-radius: 15px; }
            QLabel { color: white; font-weight: bold; border: none; background: transparent; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl = QLabel("📤 Export Election Data")
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl)

        self.radio_pdf = QRadioButton("Official PDF Report (Formatted)")
        self.radio_pdf.setChecked(True)
        self.radio_pdf.setStyleSheet("color: white; border: none; background: transparent;")
        layout.addWidget(self.radio_pdf)

        layout.addStretch()

        btns = QHBoxLayout()
        self.export_btn = QPushButton("Save to PC")
        self.cancel_btn = QPushButton("Cancel")
        self.export_btn.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px; border-radius: 8px; font-weight: bold; border: none;")
        self.cancel_btn.setStyleSheet(
            "background-color: #485460; color: white; padding: 10px; border-radius: 8px; font-weight: bold; border: none;")
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.export_btn)
        layout.addLayout(btns)


class ResultsDashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_frame.setStyleSheet(
            "background: rgba(255, 255, 255, 0.02); border-bottom: 1px solid rgba(255, 255, 255, 0.08);")
        header_layout = QHBoxLayout(header_frame)

        title_box = QVBoxLayout()
        self.main_title = QLabel("📊 Live Standings")
        self.main_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.main_title.setStyleSheet("color: white; border: none; background: transparent;")
        title_box.addWidget(self.main_title)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        filter_box = QVBoxLayout()
        self.position_filter = QComboBox()
        self.position_filter.setFixedWidth(250)
        self.position_filter.setFixedHeight(40)
        self.position_filter.addItem("Show All Positions")
        self.position_filter.setStyleSheet("""
            QComboBox { background: rgba(0,0,0,0.15); color: white; border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.2); }
            QComboBox QAbstractItemView { background-color: #1e293b; color: white; selection-background-color: #3498db; }
        """)

        fl_lbl = QLabel("FILTER POSITION")
        fl_lbl.setStyleSheet(
            "color: #2ecc71; font-size: 10px; font-weight: bold; background: transparent; border: none;")
        filter_box.addWidget(fl_lbl)
        filter_box.addWidget(self.position_filter)
        header_layout.addLayout(filter_box)
        layout.addWidget(header_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_layout.setSpacing(20)
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

    def create_position_card(self, position, candidates):
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; }")
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel(position.upper())
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setStyleSheet(
            "color: #f1c40f; border: none; border-left: 4px solid #f1c40f; padding-left: 15px; background: transparent;")
        layout.addWidget(lbl)

        table = QTableWidget(len(candidates), 3)
        table.setHorizontalHeaderLabels(["RANK", "CANDIDATE NAME", "TOTAL VOTES"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        table.setStyleSheet("""
            QTableWidget { background: transparent; border: none; color: white; } 
            QHeaderView::section { background: rgba(255, 255, 255, 0.05); color: #2ecc71; font-weight: bold; border: none; padding: 5px; }
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.setFixedHeight(45 + (len(candidates) * 50))

        for i, (name, votes) in enumerate(candidates):
            rank_text = "🏆 WINNER" if i == 0 and votes > 0 else f"#{i + 1}"
            table.setItem(i, 0, QTableWidgetItem(rank_text))
            table.setItem(i, 1, QTableWidgetItem(f"   {name}"))
            table.setItem(i, 2, QTableWidgetItem(str(votes)))
            if i == 0 and votes > 0:
                for col in range(3):
                    table.item(i, col).setForeground(QBrush(QColor("#f1c40f")))
                    table.item(i, col).setBackground(QBrush(QColor(241, 196, 15, 15)))

        layout.addWidget(table)
        return card