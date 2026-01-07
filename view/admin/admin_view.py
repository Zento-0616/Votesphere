import os, sys, random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace("\\", "/")

class SnowFallBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.snowflakes = [{'x': random.randint(0, 3000), 'y': random.randint(-50, 2000), 'size': random.randint(1, 3), 'speed': random.uniform(0.5, 1.5)} for _ in range(80)]
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_snow); self.timer.start(30)
    def update_snow(self):
        for f in self.snowflakes:
            f['y'] += f['speed']
            if f['y'] > self.height(): f['y'] = -10; f['x'] = random.randint(0, self.width())
        self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(100, 200, 255, 40)); p.setPen(Qt.PenStyle.NoPen)
        for f in self.snowflakes: p.drawEllipse(int(f['x']), int(f['y']), f['size'], f['size'])

class SidebarShimmerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._shimmer_pos, self._is_hovering, self._is_active = -100, False, False
        self._timer = QTimer(self); self._timer.timeout.connect(self.update); self._timer.setInterval(16)
        self.setStyleSheet("QPushButton { background: transparent; color: white; text-align: left; padding: 15px 25px; border-radius: 10px; margin: 4px 8px; font-size: 14px; font-weight: 500; border: none; }")
    def set_active(self, active):
        self._is_active = active
        if active: self._timer.start()
        elif not self._is_hovering: self._timer.stop()
        self.update()
    def enterEvent(self, event): self._is_hovering = True; self._timer.start(); super().enterEvent(event)
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(8, 4, -8, -4); path = QPainterPath(); path.addRoundedRect(rect, 10, 10)
        if self._is_active: p.fillPath(path, QColor(26, 188, 156))
        elif self._is_hovering: p.fillPath(path, QColor(52, 152, 219, 80))
        if self._is_hovering or self._is_active:
            self._shimmer_pos += 4
            if self._shimmer_pos > self.width(): self._shimmer_pos = -100
            grad = QLinearGradient(self._shimmer_pos, 0, self._shimmer_pos + 60, 0)
            grad.setColorAt(0, QColor(255,255,255,0)); grad.setColorAt(0.5, QColor(255,255,255,100)); grad.setColorAt(1, QColor(255,255,255,0))
            p.fillPath(path, QBrush(grad))
        p.setPen(QColor("white")); p.drawText(self.rect().adjusted(40, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())

class RotatingFrame(QFrame):
    def __init__(self, title, color_hex):
        super().__init__()
        self.base_color = QColor(color_hex); self.angle = 0
        layout = QVBoxLayout(self); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl = QLabel(title); self.title_lbl.setStyleSheet(f"color: {color_hex}; font-size: 14px; font-weight: bold; background: transparent; border:none;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_lbl = QLabel("0"); self.value_lbl.setStyleSheet("color: white; font-size: 48px; font-weight: bold; background: transparent; border:none;")
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_lbl); layout.addWidget(self.value_lbl)
        self.timer = QTimer(self); self.timer.timeout.connect(self.animate); self.timer.start(20)
    def animate(self): self.angle -= 4; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(4, 4, -4, -4); path = QPainterPath(); path.addRoundedRect(rect, 20, 20)
        p.fillPath(path, QColor(15, 23, 42, 200))
        pen = QPen(); pen.setWidth(4); grad = QConicalGradient(rect.center(), self.angle)
        grad.setColorAt(0, self.base_color); grad.setColorAt(0.5, QColor("white")); grad.setColorAt(1, self.base_color)
        pen.setBrush(QBrush(grad)); p.setPen(pen); p.drawPath(path)

class TopCandidatesGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(350); self.data = []; self.target_votes = {}; self.animated_votes = {}
        self.anim_timer = QTimer(self); self.anim_timer.timeout.connect(self.animate_step); self.anim_timer.start(16)
    def animate_step(self):
        for k, v in self.target_votes.items():
            if k not in self.animated_votes: self.animated_votes[k] = 0.0
            self.animated_votes[k] += (v - self.animated_votes[k]) * 0.1
        self.update()
    def update_data(self, new_data):
        self.data = new_data
        for name, votes, pos in self.data: self.target_votes[f"{name}_{pos}"] = votes
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("white")); p.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        p.drawText(10, 30, "🏆 Leaderboard Standings")
        if not self.data: return
        max_v = max([v for _, v, _ in self.data]) if self.data else 1
        curr_y = 60
        for name, votes, pos in self.data[:8]:
            p.setPen(QColor("#cbd5e1")); p.setFont(QFont("Segoe UI", 10))
            p.drawText(10, curr_y + 20, f"{pos}: {name}")
            val = self.animated_votes.get(f"{name}_{pos}", 0.0)
            bar_w = int((val / max_v) * (self.width() - 250)) if max_v > 0 else 0
            p.setBrush(QColor(52, 152, 219, 180)); p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(200, curr_y + 5, max(bar_w, 5), 25, 5, 5)
            p.setPen(QColor("white")); p.drawText(210 + bar_w, curr_y + 22, str(int(val)))
            curr_y += 35

class AdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoteSphere - Admin Dashboard"); self.setMinimumSize(1280, 800)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")
        self.sidebar_buttons = []; self.setup_ui()
    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        self.snow = SnowFallBackground(central)
        sidebar = QFrame(); sidebar.setFixedWidth(260); sidebar.setStyleSheet("QFrame { background: #1e293b; border-right: 1px solid #334155; }")
        sidebar_layout = QVBoxLayout(sidebar)
        logo = QLabel(); path = resource_path("assets/logo.png")
        if os.path.exists(path): logo.setPixmap(QPixmap(path).scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio))
        sidebar_layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        sidebar_layout.addSpacing(20)
        menus = ["📊 Dashboard", "👥 Candidates", "👤 Voters", "📈 Results", "🛡️ Audit Log", "⚙️ Settings"]
        for text in menus:
            btn = SidebarShimmerButton(text); sidebar_layout.addWidget(btn); self.sidebar_buttons.append(btn)
        sidebar_layout.addStretch()
        self.logout_btn = QPushButton("Logout"); self.logout_btn.setStyleSheet("background: #e74c3c; color: white; padding: 15px; font-weight: bold; border: none;")
        sidebar_layout.addWidget(self.logout_btn)
        main_layout.addWidget(sidebar)
        self.stacked = QStackedWidget(); main_layout.addWidget(self.stacked)
        self.dashboard_widget = self.create_dashboard_ui()
        self.stacked.addWidget(self.dashboard_widget)
    def create_dashboard_ui(self):
        w = QWidget(); layout = QVBoxLayout(w); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(30)
        self.title_lbl = QLabel("School Election 2025"); self.title_lbl.setStyleSheet("color: white; font-size: 42px; font-weight: bold;")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.title_lbl)
        stats_layout = QHBoxLayout(); stats_layout.setSpacing(25)
        self.voters_frame = RotatingFrame("TOTAL VOTERS", "#3498db")
        self.votes_frame = RotatingFrame("VOTES CAST", "#2ecc71")
        self.status_frame = RotatingFrame("STATUS", "#e74c3c")
        self.timer_frame = RotatingFrame("TIME LEFT", "#f1c40f")
        for f in [self.voters_frame, self.votes_frame, self.status_frame, self.timer_frame]: stats_layout.addWidget(f)
        layout.addLayout(stats_layout)
        self.graph = TopCandidatesGraph()
        graph_container = QFrame(); graph_container.setStyleSheet("background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 20px;")
        gl = QVBoxLayout(graph_container); gl.addWidget(self.graph); layout.addWidget(graph_container)
        ctrl_layout = QHBoxLayout(); btn_style = "QPushButton { background: %s; color: white; padding: 20px; border-radius: 12px; font-weight: bold; font-size: 16px; }"
        self.start_btn = QPushButton("▶ START ELECTION"); self.start_btn.setStyleSheet(btn_style % "#27ae60")
        self.stop_btn = QPushButton("⏹ STOP ELECTION"); self.stop_btn.setStyleSheet(btn_style % "#e74c3c")
        ctrl_layout.addWidget(self.start_btn); ctrl_layout.addWidget(self.stop_btn); layout.addLayout(ctrl_layout)
        return w