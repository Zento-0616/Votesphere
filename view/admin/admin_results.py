import sys
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QRadioButton, QMessageBox, QScrollArea, QFrame,
                             QFileDialog, QAbstractItemView)
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ExportResultsDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Export Election Results")
        self.setFixedSize(350, 200)
        self.setStyleSheet(
            "QDialog { background: #2c3e50; color: white; } QLabel, QRadioButton { color: white; font-size: 14px; } QPushButton { background: #3498db; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold; } QPushButton:hover { background: #2980b9; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Select export format:"))

        self.radio_pdf = QRadioButton("PDF Document (Read-Only)")
        self.radio_pdf.setChecked(True)
        layout.addWidget(self.radio_pdf)

        layout.addStretch()
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        export_btn = QPushButton("💾 Export PDF")
        export_btn.clicked.connect(self.export)
        buttons_layout.addWidget(export_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #e74c3c;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    def export(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Election Results",
                                                  f"Election_Results_{datetime.now().strftime('%Y%m%d')}.pdf",
                                                  "PDF Files (*.pdf)")
        if not filename: return

        try:
            self.generate_pdf(filename)
            self.db.log_audit("admin", "Exported election results to PDF")
            QMessageBox.information(self, "Success", f"Results exported successfully to:\n{filename}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export file:\n{str(e)}")

    def generate_pdf(self, filename):
        cursor = self.db.conn.cursor()
        election_name = self.db.get_config('election_name') or "Election Results"

        cursor.execute("SELECT position, name, grade, votes FROM candidates ORDER BY position, votes DESC")
        rows = cursor.fetchall()

        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        try:
            logo = Image("logo1.png", width=150, height=150)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
        except Exception as e:
            print(f"Logo not found or error: {e}")

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, alignment=1, spaceAfter=20,
                                     textColor=colors.darkblue)
        elements.append(Paragraph(election_name, title_style))

        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=30)
        elements.append(
            Paragraph(f"Official Results - Generated on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))

        data = [['Position', 'Candidate Name', 'Grade', 'Votes', 'Status']]
        position_max_votes = {}
        for row in rows:
            pos, _, _, v = row
            if pos not in position_max_votes:
                position_max_votes[pos] = v
            else:
                position_max_votes[pos] = max(position_max_votes[pos], v)

        for row in rows:
            status = "WINNER" if row[3] > 0 and row[3] == position_max_votes[row[0]] else ""
            data.append([row[0], row[1], row[2], str(row[3]), status])

        table = Table(data, colWidths=[120, 150, 80, 60, 100])
        style = TableStyle(
            [('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
             ('FONTSIZE', (0, 0), (-1, 0), 12), ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
             ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke), ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        for i, row in enumerate(data):
            if i == 0: continue
            if row[4] == "WINNER":
                style.add('BACKGROUND', (0, i), (-1, i), colors.lightgreen)
                style.add('TEXTCOLOR', (0, i), (-1, i), colors.black)
                style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')

        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        elements.append(
            Paragraph("This document is an official record generated by VoteSphere. It is read-only. Created By: Reynaldo M. Seroje", footer_style))
        doc.build(elements)


class ResultsDashboard(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_results()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_results)
        self.timer.start(2000)

    def setup_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 10)
        title = QLabel("📊 Live Election Results")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background: rgba(255,255,255,0.1); width: 10px; margin: 0px; border-radius: 5px; } QScrollBar::handle:vertical { background: rgba(255,255,255,0.3); border-radius: 5px; min-height: 20px; }")
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(30, 10, 30, 30)
        self.results_layout.setSpacing(20)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

        self.update_label = QLabel("Last updated: --")
        self.update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_label.setStyleSheet("color: rgba(255,255,255,0.7); font-weight: bold; padding: 10px;")
        layout.addWidget(self.update_label)

    def load_results(self):
        scroll_pos = self.scroll_area.verticalScrollBar().value()

        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            positions = [row[0] for row in cursor.fetchall()]

            if not positions:
                no_data = QLabel("No active candidates or positions found.")
                no_data.setStyleSheet("color: white; font-size: 18px; padding: 20px;")
                no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_layout.addWidget(no_data)
                return

            for position in positions:
                position_frame = QFrame()
                position_frame.setStyleSheet(
                    "QFrame { background: rgba(0,0,0,0.1); border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); }")
                frame_layout = QVBoxLayout(position_frame)
                frame_layout.setContentsMargins(15, 15, 15, 15)
                frame_layout.setSpacing(10)

                pos_title = QLabel(f"🏆 {position}")
                pos_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
                pos_title.setStyleSheet("color: #f1c40f; border: none; background: transparent;")
                frame_layout.addWidget(pos_title)

                cursor.execute("SELECT name, votes FROM candidates WHERE position = ? ORDER BY votes DESC", (position,))
                candidates_data = cursor.fetchall()

                table = QTableWidget()
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["Rank", "Candidate Name", "Total Votes"])
                table.verticalHeader().setVisible(False)
                table.setRowCount(len(candidates_data))
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

                row_height = 40
                table.verticalHeader().setDefaultSectionSize(row_height)
                header_height = 35
                total_height = header_height + (len(candidates_data) * row_height) + 5
                table.setMinimumHeight(total_height)
                table.setMaximumHeight(total_height)

                table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
                table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
                table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

                table.setStyleSheet(
                    f"QTableWidget {{ background: rgba(0,0,0,0.2); border: none; gridline-color: rgba(255,255,255,0.1); color: white; font-size: 14px; }} QHeaderView::section {{ background: rgba(255,255,255,0.15); color: white; padding: 0px; height: {header_height}px; border: none; font-weight: bold; }} QTableWidget::item {{ padding-left: 10px; }}")

                max_votes = candidates_data[0][1] if candidates_data else 0
                for i, (name, votes) in enumerate(candidates_data):
                    rank_item = QTableWidgetItem(str(i + 1))
                    rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(i, 0, rank_item)
                    table.setItem(i, 1, QTableWidgetItem(name))
                    vote_item = QTableWidgetItem(str(votes))
                    vote_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(i, 2, vote_item)

                    if i == 0 and votes > 0:
                        for col in range(3):
                            item = table.item(i, col)
                            item.setBackground(QColor(241, 196, 15, 50))
                            item.setForeground(QBrush(QColor("#f0efeb")))

                frame_layout.addWidget(table)
                self.results_layout.addWidget(position_frame)

            self.update_label.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            self.scroll_area.verticalScrollBar().setValue(scroll_pos)

        except Exception as e:
            print(f"Error loading results: {e}")