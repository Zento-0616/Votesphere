import os
import sys
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QFrame, QLabel, QPushButton, QScrollArea,
                             QButtonGroup, QRadioButton, QDialog, QGraphicsDropShadowEffect, QSplitter)
from PyQt6.QtGui import (QPixmap, QPainter, QBrush, QPen, QFont, QColor, QPainterPath, QLinearGradient)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace("\\", "/")

class SnowFallBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.snowflakes = [{'x': random.randint(0, 1920), 'y': random.randint(-50, 1080), 'size': random.randint(1, 3), 'speed': random.uniform(0.5, 1.5)} for _ in range(80)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_snow)
        self.timer.start(30)

    def update_snow(self):
        for flake in self.snowflakes:
            flake['y'] += flake['speed']
            if flake['y'] > self.height():
                flake['y'] = -10
                flake['x'] = random.randint(0, self.width())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(100, 200, 255, 40))
        for flake in self.snowflakes:
            painter.drawEllipse(int(flake['x']), int(flake['y']), flake['size'], flake['size'])

class GlowPositionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        self._hover_alpha = 0
        self._is_hovering = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.setInterval(16)

    def enterEvent(self, event):
        self._is_hovering = True
        self._timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovering = False
        self._timer.stop()
        self.update()
        super().leaveEvent(event)

    def _animate(self):
        if self._is_hovering:
            if self._hover_alpha < 40: self._hover_alpha += 5
            else: self._timer.stop()
        else:
            if self._hover_alpha > 0: self._hover_alpha -= 5
            else: self._timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        bg_color = QColor("#3498db") if self.isChecked() else QColor(255, 255, 255, 15)
        text_color = QColor("white") if (self.isChecked() or self._hover_alpha > 0) else QColor("#bdc3c7")
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, bg_color)
        if self._hover_alpha > 0:
            glow = QLinearGradient(0, 0, rect.width(), 0)
            glow.setColorAt(0.0, QColor(255, 255, 255, self._hover_alpha))
            glow.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.fillPath(path, QBrush(glow))
        if self.isChecked():
            bar_rect = QRectF(0, 5, 5, rect.height() - 10)
            bar_path = QPainterPath()
            bar_path.addRoundedRect(bar_rect, 2, 2)
            painter.fillPath(bar_path, QColor("#2ecc71"))
        painter.setPen(text_color)
        font = self.font()
        font.setPixelSize(13)
        font.setWeight(QFont.Weight.Bold if self.isChecked() else QFont.Weight.Normal)
        painter.setFont(font)
        painter.drawText(rect.adjusted(15, 0, -5, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())

class BallotSubmitAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()
        self.paper_y = 0
        self.paper_alpha = 255
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_step)
        self.timer.setInterval(16)

    def start_animation(self):
        self.paper_y = -150
        self.paper_alpha = 255
        self.raise_()
        self.show()
        self.timer.start()

    def stop_animation(self):
        self.timer.stop()
        self.hide()

    def animate_step(self):
        if self.paper_y < 50: self.paper_y += 5
        else:
            self.paper_alpha -= 10
            if self.paper_alpha <= 0:
                self.paper_y = -150
                self.paper_alpha = 255
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(15, 23, 42, 200))
        cx, cy = self.width() // 2, self.height() // 2
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        painter.drawText(QRectF(0, cy + 140, self.width(), 50), Qt.AlignmentFlag.AlignCenter, "Submitting Official Ballot...")
        box_w, box_h = 160, 140
        slit_y = cy - box_h // 2 + 30
        painter.setBrush(QColor("#1e293b"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(cx - box_w // 2 + 10, slit_y, box_w - 20, box_h))
        paper_rect = QRectF(cx - 50, slit_y + self.paper_y, 100, 130)
        painter.save()
        painter.setBrush(QColor(255, 255, 255, self.paper_alpha))
        painter.setPen(QPen(QColor("#bdc3c7"), 2))
        painter.drawRect(paper_rect)
        if self.paper_alpha > 100:
            painter.setPen(QPen(QColor("#3498db"), 4))
            painter.drawLine(QPointF(cx - 15, slit_y + self.paper_y + 90), QPointF(cx, slit_y + self.paper_y + 105))
            painter.drawLine(QPointF(cx, slit_y + self.paper_y + 105), QPointF(cx + 30, slit_y + self.paper_y + 75))
        painter.restore()
        painter.setBrush(QColor("#334155"))
        painter.drawRoundedRect(QRectF(cx - box_w // 2, slit_y, box_w, box_h), 5, 5)
        painter.setBrush(QColor("#475569"))
        painter.drawRoundedRect(QRectF(cx - box_w // 2 - 10, slit_y - 20, box_w + 20, 20), 5, 5)
        painter.setPen(QColor(255, 255, 255, 60))
        painter.setFont(QFont("Segoe UI", 30))
        painter.drawText(QRectF(cx - box_w // 2, slit_y, box_w, box_h), Qt.AlignmentFlag.AlignCenter, "✓")

class UrgentTimerFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 90)
        self.current_color = QColor("#3498db")
        self.glow_alpha = 100
        self.glow_dir = 5
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 5, 0, 5)
        self.lbl_title = QLabel("TIME REMAINING")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498db; background: transparent;")
        self.lbl_time = QLabel("--:--")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 32px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_time)

    def update_time(self, text):
        self.lbl_time.setText(text)

    def set_urgent(self, urgent):
        self.current_color = QColor("#e74c3c") if urgent else QColor("#3498db")
        self.lbl_title.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {self.current_color.name()}; background: transparent;")
        self.timer.setInterval(20 if urgent else 50)

    def animate(self):
        self.glow_alpha += self.glow_dir
        if self.glow_alpha >= 200 or self.glow_alpha <= 50: self.glow_dir *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect().adjusted(2, 2, -2, -2))
        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)
        bg_color = QColor(self.current_color)
        bg_color.setAlpha(40)
        painter.fillPath(path, bg_color)
        pen = QPen(QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), self.glow_alpha))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path)

class VoteReceiptDialog(QDialog):
    def __init__(self, candidate_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vote Receipt")
        self.setFixedSize(420, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #1e293b; border: 2px solid #3498db; border-radius: 20px; }")
        layout.addWidget(frame)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(25, 30, 25, 30)
        icon = QLabel("✓")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI", 48))
        icon.setStyleSheet("border: none; background: transparent; color: #2ecc71;")
        fl.addWidget(icon)
        title = QLabel("VOTE RECORDED")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none; background: transparent; letter-spacing: 1px;")
        fl.addWidget(title)
        instr_frame = QFrame()
        instr_frame.setStyleSheet("background-color: rgba(52, 152, 219, 0.1); border-radius: 8px; border: 1px dashed #3498db;")
        instr_layout = QHBoxLayout(instr_frame)
        instr_lbl = QLabel("Please capture a photo of this receipt for your records before exiting.")
        instr_lbl.setWordWrap(True)
        instr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instr_lbl.setStyleSheet("color: #3498db; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        instr_layout.addWidget(instr_lbl)
        fl.addWidget(instr_frame)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        cl = QVBoxLayout(container)
        for pos, name in candidate_list:
            row = QFrame()
            row.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; }")
            rl = QVBoxLayout(row)
            p_lbl = QLabel(pos)
            p_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; text-transform: uppercase; border: none; background: transparent;")
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border: none; background: transparent;")
            rl.addWidget(p_lbl); rl.addWidget(n_lbl)
            cl.addWidget(row)
        cl.addStretch()
        scroll.setWidget(container)
        fl.addWidget(scroll)
        btn = QPushButton("EXIT PORTAL")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("QPushButton { background-color: #334155; color: white; font-weight: bold; font-size: 15px; border-radius: 10px; border: 1px solid #475569; }")
        btn.clicked.connect(self.accept)
        fl.addWidget(btn)

class CustomPopup(QDialog):
    def __init__(self, parent, title, message, icon_type="info", ok_text="OK", cancel_text="Cancel"):
        super().__init__(parent)
        self.setFixedSize(400, 280)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        color = "#3498db"
        icon = "ℹ"
        if icon_type == "success": color, icon = "#2ecc71", "✓"
        elif icon_type == "error": color, icon = "#e74c3c", "!"
        elif icon_type == "warning": color, icon = "#f1c40f", "⚠"
        elif icon_type == "question": color, icon = "#3498db", "?"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background: #0f172a; border-radius: 12px; border: 2px solid {color}; }} QLabel {{ color: white; border: none; }}")
        layout.addWidget(frame)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(20, 20, 20, 20)
        hl = QHBoxLayout()
        il = QLabel(icon)
        il.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        tl = QLabel(title)
        tl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        tl.setStyleSheet(f"color: {color};")
        hl.addWidget(il); hl.addWidget(tl); hl.addStretch()
        fl.addLayout(hl)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setFont(QFont("Arial", 11))
        msg.setStyleSheet("color: #ecf0f1;")
        msg.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(msg)
        fl.addWidget(scroll)
        bl = QHBoxLayout()
        bl.addStretch()
        if icon_type == "question":
            y = QPushButton(ok_text)
            y.setStyleSheet(f"background: {color}; color: white; font-weight: bold; padding: 8px 25px; border-radius: 6px; border:none;")
            y.clicked.connect(self.accept)
            n = QPushButton(cancel_text)
            n.setStyleSheet("background: #334155; color: white; padding: 8px 25px; border-radius: 6px; border:none;")
            n.clicked.connect(self.reject)
            bl.addWidget(y); bl.addWidget(n)
        else:
            o = QPushButton(ok_text)
            o.setStyleSheet(f"background: {color}; color: white; font-weight: bold; padding: 8px 25px; border-radius: 6px; border:none;")
            o.clicked.connect(self.accept)
            bl.addWidget(o)
        fl.addLayout(bl)

class VoterDashboardView(QMainWindow):
    def __init__(self, user_name):
        super().__init__()
        self.user_name = user_name
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("VoteSphere - Voter Dashboard")
        self.setStyleSheet("QMainWindow { background: #0f172a; }")
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.snow = SnowFallBackground(central)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("QFrame { background-color: #1e293b; border-right: 1px solid rgba(255,255,255,0.1); }")
        self.sl = QVBoxLayout(self.sidebar)
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path = resource_path("assets/logo.png")
        if os.path.exists(path): self.logo.setPixmap(QPixmap(path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else: self.logo.setText("✓"); self.logo.setFont(QFont("Arial", 40)); self.logo.setStyleSheet("color: #3498db;")
        self.sl.addWidget(self.logo)
        self.lbl_welcome = QLabel(f"Welcome,\n{self.user_name}")
        self.lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_welcome.setStyleSheet("color: #ecf0f1; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.sl.addWidget(self.lbl_welcome)
        self.sl.addWidget(QLabel("POSITIONS:", styleSheet="color:white;"))
        self.scroll_pos = QScrollArea()
        self.scroll_pos.setWidgetResizable(True)
        self.scroll_pos.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.widget_pos = QWidget()
        self.layout_pos = QVBoxLayout(self.widget_pos)
        self.layout_pos.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_pos.setWidget(self.widget_pos)
        self.sl.addWidget(self.scroll_pos)
        self.lbl_summary = QLabel("0 selected")
        self.lbl_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_summary.setStyleSheet("color: #3498db; font-weight: bold; font-size: 12px;")
        self.sl.addWidget(self.lbl_summary)
        self.btn_submit = QPushButton("SUBMIT BALLOT")
        self.btn_submit.setStyleSheet("QPushButton { background: #3498db; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; font-size: 14px; } QPushButton:hover { background: #2980b9; } QPushButton:disabled { background: #334155; }")
        self.sl.addWidget(self.btn_submit)
        self.btn_logout = QPushButton("LOGOUT")
        self.btn_logout.setStyleSheet("QPushButton { background: rgba(231, 76, 60, 0.1); color: #e74c3c; font-weight: bold; border: 1px solid #e74c3c; padding: 10px; border-radius: 6px; font-size: 12px; } QPushButton:hover { background: #e74c3c; color: white; }")
        self.sl.addWidget(self.btn_logout)
        self.main_layout.addWidget(self.sidebar)
        content = QWidget()
        cl = QVBoxLayout(content)
        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(QLabel("Cast Your Official Vote", styleSheet="color:white; font-size:32px; font-weight:bold;"))
        title_box.addWidget(QLabel("Please select ONE candidate for each required position.", styleSheet="color:#94a3b8; font-size:16px;"))
        top_bar.addLayout(title_box)
        self.timer_frame = UrgentTimerFrame()
        top_bar.addWidget(self.timer_frame)
        cl.addLayout(top_bar)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        cand_frame = QFrame()
        cf = QVBoxLayout(cand_frame)
        self.lbl_current_pos = QLabel("Position View")
        self.lbl_current_pos.setStyleSheet("font-size: 22px; font-weight: bold; color: #3498db; margin-bottom: 10px; border-left: 5px solid #3498db; padding-left: 10px;")
        cf.addWidget(self.lbl_current_pos)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: rgba(30, 41, 59, 0.5); border-radius: 10px; }")
        self.widget_cand = QWidget()
        self.layout_cand = QVBoxLayout(self.widget_cand)
        self.layout_cand.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.widget_cand)
        cf.addWidget(scroll)
        leader_wrapper = QFrame()
        leader_wrapper.setFixedWidth(340)
        lw = QVBoxLayout(leader_wrapper)
        lw.addWidget(QLabel("VOTING TRENDS", styleSheet="font-size: 20px; font-weight: bold; color: #94a3b8; border-left: 5px solid #94a3b8; padding-left: 10px;"))
        self.leaders_widget = QWidget()
        self.leaders_layout = QVBoxLayout(self.leaders_widget)
        self.leaders_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ls = QScrollArea()
        ls.setWidgetResizable(True)
        ls.setStyleSheet("background: transparent; border: none;")
        ls.setWidget(self.leaders_widget)
        lw.addWidget(ls)
        splitter.addWidget(cand_frame)
        splitter.addWidget(leader_wrapper)
        splitter.setStretchFactor(0, 4)
        cl.addWidget(splitter)
        self.main_layout.addWidget(content)
        self.submit_animation = BallotSubmitAnimation(central)

    def resizeEvent(self, event):
        self.submit_animation.resize(self.width(), self.height())
        self.snow.resize(self.width(), self.height())
        super().resizeEvent(event)

    def apply_glow(self, frame, selected):
        shadow = QGraphicsDropShadowEffect(self)
        if selected: shadow.setBlurRadius(40); shadow.setColor(QColor("#3498db")); shadow.setOffset(0, 0)
        else: shadow.setBlurRadius(15); shadow.setColor(QColor(0, 0, 0, 80)); shadow.setOffset(3, 3)
        frame.setGraphicsEffect(shadow)