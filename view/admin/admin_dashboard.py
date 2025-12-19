from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QFrame, QLabel, QPushButton, QStackedWidget, QMessageBox,
                             QScrollArea, QSizePolicy, QDialog, QFormLayout,
                             QLineEdit, QDateEdit, QSpinBox, QFileDialog)
from PyQt6.QtGui import (QFont, QPainter, QColor, QBrush, QPixmap, QPen,
                         QConicalGradient, QPainterPath, QPolygonF, QLinearGradient,
                         QIntValidator)  # Added QIntValidator
from PyQt6.QtCore import Qt, QTimer, QDateTime, QRectF, QPointF, QDate

from view.admin.admin_candidates import ManageCandidates
from view.admin.admin_voters import ManageVoters
from view.admin.admin_results import ResultsDashboard, ExportResultsDialog
from view.admin.admin_settings import SettingsWindow
from view.admin.admin_audit import AuditLogViewer


# ELECTION SETUP DIALOG
class ElectionSetupDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Start New Election")
        self.setFixedSize(600, 350)
        self.setStyleSheet("""
            QDialog { background: #2c3e50; color: white; }
            QLabel { font-size: 14px; font-weight: bold; color: white; }
            QLineEdit, QDateEdit {
                background: #ecf0f1; border-radius: 5px; padding: 8px;
                color: #2c3e50; font-weight: bold; font-size: 14px;
            }
            QPushButton {
                padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Configure Election Settings")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 22px; color: #f1c40f; margin-bottom: 15px; font-weight: bold;")
        layout.addWidget(header)

        # Form
        form = QFormLayout()
        form.setSpacing(20)

        self.name_input = QLineEdit()
        self.name_input.setText(self.db.get_config('election_name') or "School Election 2025")
        form.addRow("Election Name:", self.name_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("Election Date:", self.date_input)

        dur_layout = QHBoxLayout()

        # Hours Input
        self.hrs_input = QLineEdit()
        self.hrs_input.setPlaceholderText("0")
        self.hrs_input.setValidator(QIntValidator(0, 999))
        self.hrs_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Minutes Input
        self.mins_input = QLineEdit()
        self.mins_input.setText("10")
        self.mins_input.setValidator(QIntValidator(0, 59))
        self.mins_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dur_layout.addWidget(self.hrs_input)
        dur_layout.addWidget(QLabel("Hrs"))
        dur_layout.addSpacing(10)
        dur_layout.addWidget(self.mins_input)
        dur_layout.addWidget(QLabel("Mins"))

        form.addRow("Duration:", dur_layout)

        layout.addLayout(form)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("background: #e74c3c; color: white; border: 1px solid rgba(255,255,255,0.3);")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        start_btn = QPushButton("✅ CONFIRM START")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.setStyleSheet("background: #27ae60; color: white; border: 1px solid rgba(255,255,255,0.3);")
        start_btn.clicked.connect(self.accept)
        btn_layout.addWidget(start_btn)

        layout.addLayout(btn_layout)

    def get_data(self):
        h_text = self.hrs_input.text()
        m_text = self.mins_input.text()

        hours = int(h_text) if h_text else 0
        minutes = int(m_text) if m_text else 0

        total_seconds = (hours * 3600) + (minutes * 60)
        return self.name_input.text(), self.date_input.date().toString("yyyy-MM-dd"), total_seconds


# SIDEBAR BUTTON
class SidebarShimmerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation variables
        self._shimmer_pos = -100
        self._is_hovering = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.setInterval(16)

        self.setStyleSheet("""
            QPushButton {
                background: transparent; 
                color: rgba(255, 255, 255, 0.9); 
                text-align: left;
                padding: 12px 20px; 
                border: none;
                border-radius: 20px;
                margin: 4px 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:pressed {
                background: rgba(20, 225, 148, 0.3); 
                color: white;
            }
        """)

    def enterEvent(self, event):
        self._is_hovering = True
        self._shimmer_pos = -100
        self._timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovering = False
        self._timer.stop()
        self.update()
        super().leaveEvent(event)

    def _animate(self):
        self._shimmer_pos += 4
        if self._shimmer_pos > self.width() + 100:
            self._shimmer_pos = -200
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self._is_hovering:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            rect = QRectF(self.rect()).adjusted(8, 4, -8, -4)
            path = QPainterPath()
            path.addRoundedRect(rect, 20, 20)

            painter.setClipPath(path)

            # Draw Hover Background
            painter.fillPath(path, QColor(52, 152, 219, 80))

            # Draw Shimmer Gradient
            gradient = QLinearGradient(self._shimmer_pos, 0, self._shimmer_pos + 50, 0)
            gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
            gradient.setColorAt(0.5, QColor(255, 255, 255, 150))
            gradient.setColorAt(1.0, QColor(255, 255, 255, 0))

            painter.fillPath(path, QBrush(gradient))


# ROTATING BORDER FRAME
class RotatingFrame(QFrame):
    def __init__(self, title, value_label, color_hex):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.base_color = QColor(color_hex)
        self.angle = 0
        self.is_active = True

        # Shimmer Animation Variables
        self.shimmer_pos = -200
        self.shimmer_speed = 10

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            f"font-weight: bold; color: {color_hex}; font-size: 28px; background: transparent; border: none;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl)

        self.value_lbl = value_label
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_lbl)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.setInterval(20)
        self.timer.start()

    def set_color(self, color_hex):
        self.base_color = QColor(color_hex)
        self.title_lbl.setStyleSheet(
            f"font-weight: bold; color: {color_hex}; font-size: 28px; background: transparent; border: none;")
        self.update()

    def animate(self):
        if not self.is_active: return

        # Rotate Border
        self.angle -= 4
        if self.angle < 0: self.angle = 360

        # Move Shimmer
        self.shimmer_pos += self.shimmer_speed
        if self.shimmer_pos > self.width() + 200:
            self.shimmer_pos = -200

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect().adjusted(4, 4, -4, -4))
        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)

        # Draw Background
        painter.fillPath(path, QColor(0, 0, 0, 60))

        # Draw Shimmer Effect
        painter.save()
        painter.setClipPath(path)

        gradient = QLinearGradient(self.shimmer_pos, 0, self.shimmer_pos + 60, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 40))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.fillPath(path, QBrush(gradient))
        painter.restore()

        # Draw Rotating Border
        pen = QPen()
        pen.setWidth(4)

        if self.is_active:
            gradient = QConicalGradient(rect.center(), self.angle)
            gradient.setColorAt(0.0, self.base_color)
            gradient.setColorAt(0.25, QColor("white"))
            gradient.setColorAt(0.5, self.base_color)
            gradient.setColorAt(1.0, self.base_color)
            pen.setBrush(QBrush(gradient))
        else:
            pen.setColor(self.base_color)

        painter.setPen(pen)
        painter.drawPath(path)


# BALLOT DROP FRAME
class BallotDropFrame(RotatingFrame):
    def __init__(self, title, value_label, color_hex):
        super().__init__(title, value_label, color_hex)
        self.drop_y = 0
        self.drop_opacity = 0
        self.is_dropping = False

        self.drop_timer = QTimer(self)
        self.drop_timer.timeout.connect(self.animate_drop)
        self.drop_timer.setInterval(20)

    def trigger_drop(self):
        if not self.is_dropping:
            self.drop_y = -20
            self.drop_opacity = 255
            self.is_dropping = True
            self.drop_timer.start()

    def animate_drop(self):
        self.drop_y += 2
        if self.drop_y > 10:
            self.drop_opacity -= 15

        if self.drop_opacity <= 0:
            self.is_dropping = False
            self.drop_timer.stop()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        icon_x = self.width() - 45
        icon_y = 35

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 60))
        painter.drawRoundedRect(icon_x, icon_y, 24, 20, 2, 2)

        painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawRoundedRect(icon_x - 2, icon_y - 4, 28, 4, 1, 1)

        if self.is_dropping:
            painter.setBrush(QColor(255, 255, 255, self.drop_opacity))
            painter.setClipRect(icon_x, icon_y - 25, 24, 25)
            painter.drawRect(icon_x + 6, icon_y + self.drop_y, 12, 16)


# URGENT TIMER FRAME
class UrgentTimerFrame(QFrame):
    def __init__(self, title, value_label):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.current_color = QColor("#f1c40f")
        self.is_active = False
        self.glow_alpha = 100
        self.glow_dir = 5

        # Shimmer Variables
        self.shimmer_pos = -200
        self.shimmer_speed = 10

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            "font-weight: bold; color: #f1c40f; font-size: 28px; background: transparent; border: none;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl)

        self.value_lbl = value_label
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_lbl)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.setInterval(50)

    def set_urgent(self, is_urgent):
        if is_urgent:
            self.current_color = QColor("#e74c3c")
            self.title_lbl.setStyleSheet(
                "font-weight: bold; color: #e74c3c; font-size: 28px; background: transparent; border: none;")
            self.title_lbl.setText("⚠️ ENDING")
            self.timer.setInterval(30)
        else:
            self.current_color = QColor("#f1c40f")
            self.title_lbl.setStyleSheet(
                "font-weight: bold; color: #f1c40f; font-size: 28px; background: transparent; border: none;")
            self.title_lbl.setText("⏳ Time Left")
            self.timer.setInterval(50)

    def set_active(self, active):
        self.is_active = active
        if active:
            self.timer.start()
        else:
            self.timer.stop();
            self.update()

    def animate(self):
        # Glow Logic
        self.glow_alpha += self.glow_dir
        if self.glow_alpha >= 255:
            self.glow_alpha = 255;
            self.glow_dir = -8
        if self.glow_alpha <= 50:
            self.glow_alpha = 50;
            self.glow_dir = 8

        # Shimmer Logic
        self.shimmer_pos += self.shimmer_speed
        if self.shimmer_pos > self.width() + 200:
            self.shimmer_pos = -200

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect().adjusted(4, 4, -4, -4))
        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)

        # Background
        painter.fillPath(path, QColor(0, 0, 0, 40))

        # Shimmer Effect
        painter.save()
        painter.setClipPath(path)

        gradient = QLinearGradient(self.shimmer_pos, 0, self.shimmer_pos + 60, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 40))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.fillPath(path, QBrush(gradient))
        painter.restore()

        # Border
        pen = QPen()
        pen.setWidth(4)

        if self.is_active:
            pen.setColor(QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(),
                                self.glow_alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), 30))
            painter.drawPath(path)
        else:
            pen.setColor(self.current_color)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)


# TOP CANDIDATES GRAPH
class TopCandidatesGraph(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.raw_data = []
        self.animated_votes = {}
        self.target_votes = {}

        self.bar_height = 35
        self.margin_top = 40
        self.setMinimumHeight(200)
        self.setStyleSheet("background: transparent;")

        self.fade_value = 255
        self.fade_direction = -5

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_step)
        self.anim_timer.start(16)

        self.update_data()

    def reset_animation(self):
        self.animated_votes.clear()
        self.update()

    def animate_step(self):
        self.fade_value += self.fade_direction
        if self.fade_value <= 100:
            self.fade_value = 100
            self.fade_direction = 5
        elif self.fade_value >= 255:
            self.fade_value = 255
            self.fade_direction = -5

        for key, target in self.target_votes.items():
            if key not in self.animated_votes:
                self.animated_votes[key] = 0.0

            current = self.animated_votes[key]

            if abs(target - current) > 0.1:
                diff = target - current
                self.animated_votes[key] += diff * 0.1
            else:
                self.animated_votes[key] = float(target)

        self.update()

    def update_data(self):
        try:
            self.raw_data = []

            cursor = self.db.conn.cursor()
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            positions = [row[0] for row in cursor.fetchall()]

            for pos in positions:
                cursor.execute(
                    "SELECT name, votes, position FROM candidates WHERE position=? ORDER BY votes DESC LIMIT 3", (pos,))
                results = cursor.fetchall()
                for res in results:
                    name, votes, position = res
                    self.raw_data.append(res)

                    key = f"{name}_{position}"
                    self.target_votes[key] = votes

                    if key not in self.animated_votes:
                        self.animated_votes[key] = 0.0

            self.raw_data.sort(key=lambda x: (x[2], -x[1]))

            total_h = self.margin_top + (len(self.raw_data) * (self.bar_height + 10)) + (len(positions) * 30) + 50
            self.setMinimumHeight(max(200, total_h))

        except Exception as e:
            print(f"Graph error: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("white"))

        font = painter.font()
        font.setPixelSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignLeft, "🏆 Current Leaders per Position (Top 3)")

        if not self.raw_data: return

        max_votes = 1
        if self.target_votes:
            max_votes = max(self.target_votes.values())
        if max_votes == 0: max_votes = 1

        text_width = 180
        available_width = self.width() - text_width - 60
        current_y = self.margin_top

        font.setPixelSize(13)
        painter.setFont(font)

        last_pos = ""
        rank_counter = 0

        for name, real_votes, position in self.raw_data:
            if position != last_pos:
                current_y += 15
                painter.setPen(QColor("#f1c40f"))
                painter.drawText(0, current_y, text_width, self.bar_height // 2, Qt.AlignmentFlag.AlignLeft,
                                 position.upper())
                current_y += 20
                last_pos = position
                rank_counter = 0

            rank_counter += 1
            painter.setPen(QColor("white"))
            painter.drawText(0, current_y + 5, text_width, self.bar_height,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{rank_counter}. {name}")

            # Background bar
            bar_x = text_width + 10
            painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(bar_x, current_y, available_width, self.bar_height, 4, 4)

            key = f"{name}_{position}"
            display_votes = self.animated_votes.get(key, 0.0)

            bar_w = max(5, int((display_votes / max_votes) * available_width))

            if rank_counter == 1:
                bar_color = QColor(241, 196, 15, self.fade_value)
            elif rank_counter == 2:
                bar_color = QColor(52, 152, 219, self.fade_value)
            elif rank_counter == 3:
                bar_color = QColor(231, 76, 60, self.fade_value)
            else:
                bar_color = QColor("#3498db")

            painter.setBrush(QBrush(bar_color))
            painter.drawRoundedRect(bar_x, current_y, bar_w, self.bar_height, 4, 4)

            # Draw Number
            num_x = bar_x + bar_w + 10
            painter.setPen(QColor("white"))
            painter.drawText(num_x, current_y, 50, self.bar_height,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             str(int(display_votes)))

            current_y += self.bar_height + 10


# ADMIN DASHBOARD
class AdminDashboard(QMainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id

        self.explicit_logout = False

        self.prev_vote_count = 0

        self.setup_ui()
        self.update_stats()
        self.check_election_status()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_stats)
        self.refresh_timer.start(2000)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_timer_display)
        self.clock_timer.start(1000)

    def setup_ui(self):
        self.setWindowTitle("VoteSphere - Admin Dashboard")
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #4ca1af
                );
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: #2c3e50; color: white;
                border-right: 2px solid #34495e;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Logo
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("logo.png")
            logo_pixmap = logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("🗳️")
            logo_label.setFont(QFont("Arial", 50))

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("padding-top: 20px; padding-bottom: 10px;")
        sidebar_layout.addWidget(logo_label)

        menu_title = QLabel("Menu")
        menu_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        menu_title.setStyleSheet("""
            background: transparent; color: white; padding: 10px;
            border-bottom: 2px solid #1a252f;
        """)
        menu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(menu_title)

        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Candidates", self.show_candidates),
            ("👤 Voters", self.show_voters),
            ("📈 Results", self.show_results),
            ("🛡️ Audit Log", self.show_audit),
            ("⚙️ Settings", self.show_settings)
        ]

        # Use Custom Shimmer Button
        for text, slot in buttons:
            btn = SidebarShimmerButton(text)
            btn.clicked.connect(slot)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c; color: white; padding: 15px;
                border: none; font-size: 16px; font-weight: bold;
                border-top: 2px solid #34495e;
            }
            QPushButton:hover { background: #c0392b; }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

        # Main content
        main_content = QWidget()
        main_content.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #4ca1af
                );
            }
        """)
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("QStackedWidget { background: transparent; }")
        main_content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(main_content)

        # Initialize pages
        self.dashboard_page = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)

        self.candidates_page = ManageCandidates(self.db)
        self.stacked_widget.addWidget(self.candidates_page)

        self.voters_page = ManageVoters(self.db)
        self.stacked_widget.addWidget(self.voters_page)

        self.results_page = ResultsDashboard(self.db)
        self.stacked_widget.addWidget(self.results_page)

        self.audit_page = AuditLogViewer(self.db)
        self.stacked_widget.addWidget(self.audit_page)

        self.settings_page = SettingsWindow(self.db)
        self.stacked_widget.addWidget(self.settings_page)

    def create_dashboard_page(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Title
        election_name = self.db.get_config('election_name') or "Admin Dashboard"
        self.title_label = QLabel(election_name)
        self.title_label.setFont(QFont("Arial", 38, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Total Voters
        self.total_voters_label = QLabel("0")
        self.total_voters_label.setStyleSheet(self.get_stat_label_style())
        self.voters_frame = RotatingFrame("👥 Total Voters", self.total_voters_label, "#3498db")
        stats_layout.addWidget(self.voters_frame)

        # Votes Cast
        self.votes_cast_label = QLabel("0")
        self.votes_cast_label.setStyleSheet(self.get_stat_label_style())
        self.votes_frame = BallotDropFrame("🗳️ Votes Cast", self.votes_cast_label, "#2ecc71")
        stats_layout.addWidget(self.votes_frame)

        # Status
        self.status_label = QLabel("INACTIVE")
        self.status_label.setStyleSheet(self.get_stat_label_style())
        self.status_frame = RotatingFrame("📊 Status", self.status_label, "#e74c3c")
        stats_layout.addWidget(self.status_frame)

        # Timer
        self.timer_label = QLabel("--:--:--")
        self.timer_label.setStyleSheet(self.get_stat_label_style())
        self.timer_frame = UrgentTimerFrame("⏳ Time Left", self.timer_label)
        stats_layout.addWidget(self.timer_frame)

        layout.addLayout(stats_layout)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background: rgba(0,0,0,0.15); margin-top: 10px; margin-bottom: 10px;")
        layout.addWidget(line)

        # Graph
        self.leaders_graph = TopCandidatesGraph(self.db)

        graph_scroll = QScrollArea()
        graph_scroll.setWidget(self.leaders_graph)
        graph_scroll.setWidgetResizable(True)
        graph_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        graph_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        graph_scroll.setMinimumHeight(350)

        graph_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: rgba(255,255,255,0.1); width: 10px; margin: 0px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: rgba(0,0,0,0.20); border-radius: 5px; min-height: 20px; }
        """)

        layout.addWidget(graph_scroll)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)

        self.start_btn = QPushButton("▶ START ELECTION")
        self.start_btn.setStyleSheet(self.get_button_style("#27ae60"))
        self.start_btn.clicked.connect(self.start_election)
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ STOP ELECTION")
        self.stop_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        self.stop_btn.clicked.connect(self.stop_election)
        controls_layout.addWidget(self.stop_btn)

        export_btn = QPushButton("📊 EXPORT RESULTS")
        export_btn.setStyleSheet(self.get_button_style("#3498db"))
        export_btn.clicked.connect(self.export_results)
        controls_layout.addWidget(export_btn)

        layout.addLayout(controls_layout)
        return widget

    def get_stat_label_style(self):
        return """
            font-size: 50px; font-weight: bold; color: white;
            background: transparent; border: none;
        """

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background: {color}; color: white; padding: 20px 25px;
                border: none; border-radius: 12px; font-weight: bold;
                font-size: 16px; border: 2px solid rgba(255,255,255,0.3);
            }}
            QPushButton:hover {{ transform: scale(1.05); }}
            QPushButton:disabled {{ background: #95a5a6; color: #bdc3c7; }}
        """

    def update_stats(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='voter'")
            total_voters = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE voted=1")
            votes_cast = cursor.fetchone()[0]
            self.total_voters_label.setText(str(total_voters))
            self.votes_cast_label.setText(str(votes_cast))

            # BALLOT DROP TRIGGER
            if votes_cast > self.prev_vote_count:
                if hasattr(self, 'votes_frame'):
                    self.votes_frame.trigger_drop()
            self.prev_vote_count = votes_cast

            if hasattr(self, 'leaders_graph'):
                self.leaders_graph.update_data()

        except Exception as e:
            print(f"Error updating stats: {e}")

    def show_dashboard(self):
        name = self.db.get_config('election_name')
        if name: self.title_label.setText(name)
        self.stacked_widget.setCurrentIndex(0)

        # RESET ANIMATION ON TAB SWITCH
        if hasattr(self, 'leaders_graph'):
            self.leaders_graph.reset_animation()

        self.update_stats()
        self.check_election_status()

    def show_candidates(self):
        self.stacked_widget.setCurrentIndex(1);
        self.candidates_page.load_candidates()

    def show_voters(self):
        self.stacked_widget.setCurrentIndex(2);
        self.voters_page.load_voters()

    def show_results(self):
        self.stacked_widget.setCurrentIndex(3);
        self.results_page.load_results()

    def show_audit(self):
        self.stacked_widget.setCurrentIndex(4)
        self.audit_page.load_logs()

    def show_settings(self):
        self.stacked_widget.setCurrentIndex(5)

    def update_timer_display(self):
        status = self.db.get_config('election_status')
        if status != 'active':
            self.timer_label.setText("--:--:--")
            return

        target_time_str = self.db.get_config('election_target_time')
        if not target_time_str:
            return

        target_time = QDateTime.fromString(target_time_str, Qt.DateFormat.ISODate)
        current_time = QDateTime.currentDateTime()

        seconds_left = current_time.secsTo(target_time)

        if seconds_left <= 0:
            self.stop_election(auto=True)
        else:
            # URGENT TIMER
            if hasattr(self, 'timer_frame'):
                if seconds_left <= 600:
                    self.timer_frame.set_urgent(True)
                else:
                    self.timer_frame.set_urgent(False)

            days = seconds_left // 86400
            rem = seconds_left % 86400
            hours = rem // 3600
            rem %= 3600
            minutes = rem // 60
            seconds = rem % 60

            if days > 0:
                self.timer_label.setText(f"{days}Day {hours:02}:{minutes:02}:{seconds:02}")
                self.timer_label.setStyleSheet(self.get_stat_label_style().replace("60px", "36px"))
            else:
                self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
                self.timer_label.setStyleSheet(self.get_stat_label_style())

    def check_election_status(self):
        status = self.db.get_config('election_status')
        if status == 'active':
            self.status_label.setText("LIVE")
            if hasattr(self, 'status_frame'):
                self.status_frame.set_color("#2ecc71")
            if hasattr(self, 'timer_frame'):
                self.timer_frame.set_active(True)

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.update_timer_display()
        else:
            self.status_label.setText("ENDED")
            if hasattr(self, 'status_frame'):
                self.status_frame.set_color("#e74c3c")
            if hasattr(self, 'timer_frame'):
                self.timer_frame.set_active(False)

            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.timer_label.setText("--:--:--")

    def start_election(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM votes")
        vote_count = cursor.fetchone()[0]

        if vote_count > 0:
            reply = QMessageBox.question(self, "Existing Data Found",
                                         "⚠️ There are existing votes in the database.\n\n"
                                         "Do you want to RESET votes and start a new election?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

            # Reset Votes Logic
            cursor.execute("DELETE FROM votes")
            cursor.execute("UPDATE candidates SET votes = 0")
            cursor.execute("UPDATE users SET voted = 0")
            self.db.conn.commit()

        dialog = ElectionSetupDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, date, duration = dialog.get_data()

            if duration <= 0:
                QMessageBox.warning(self, "Invalid Time", "Duration must be at least 1 minute.")
                return

            self.db.update_config('election_name', name)
            self.db.update_config('election_date', date)
            self.db.update_config('election_duration', duration)

            target_time = QDateTime.currentDateTime().addSecs(duration)
            self.db.update_config('election_target_time', target_time.toString(Qt.DateFormat.ISODate))

            self.db.update_config('election_status', 'active')
            self.db.log_audit("admin", "Started Election")

            if hasattr(self, 'title_label'):
                self.title_label.setText(name)

            self.check_election_status()
            self.update_stats()

            QMessageBox.information(self, "Election Started",
                                    f"✅ Election '{name}' is now LIVE!\nDuration: {duration // 60} mins")

    def stop_election(self, auto=False):
        if auto:
            self.db.update_config('election_status', 'inactive')
            self.db.update_config('election_target_time', "")
            self.check_election_status()

            try:
                filename = f"Election_Results_Final_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.pdf"
                exporter = ExportResultsDialog(self.db)
                exporter.generate_pdf(filename)
                QMessageBox.information(self, "Time's Up",
                                        f"Election ended automatically.\nResults saved to:\n{filename}")
            except Exception as e:
                print(f"Auto-export failed: {e}")
            return

        # MANUAL STOP
        if QMessageBox.question(self, "Stop Election",
                                "Are you sure you want to stop the election?\n\n"
                                "This will end voting and generate the results PDF.") == QMessageBox.StandardButton.Yes:

            self.db.update_config('election_status', 'inactive')
            self.db.update_config('election_target_time', "")
            self.check_election_status()

            default_name = f"Election_Results_{QDateTime.currentDateTime().toString('yyyy-MM-dd_HHmm')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Official Results", default_name, "PDF Files (*.pdf)")

            if file_path:
                try:
                    exporter = ExportResultsDialog(self.db)
                    exporter.generate_pdf(file_path)
                    QMessageBox.information(self, "Success", f"Election stopped.\nReport saved to:\n{file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to save PDF:\n{e}")
            else:
                QMessageBox.information(self, "Election Stopped", "Election stopped (No report generated).")

    def export_results(self):
        dialog = ExportResultsDialog(self.db)
        dialog.exec()

    def closeEvent(self, event):
        if self.explicit_logout:
            event.accept()
            return

        reply = QMessageBox.question(self, "Confirm Exit",
                                     "Do you really want to log out?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def logout(self):
        if QMessageBox.question(self, "Confirm", "Logout?") == QMessageBox.StandardButton.Yes:
            self.explicit_logout = True
            from view.common.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()