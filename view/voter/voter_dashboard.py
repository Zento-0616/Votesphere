from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QFrame, QLabel, QPushButton, QScrollArea,
                             QButtonGroup, QRadioButton, QDialog, QSizePolicy,
                             QApplication, QSplitter, QGraphicsDropShadowEffect)
from PyQt6.QtGui import (QPixmap, QPainter, QBrush, QPen, QFont, QColor,
                         QPainterPath, QLinearGradient)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QRectF, QPointF
import random


#  SNOWFALL ANIMATION
class SnowFallOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.snowflakes = []
        for _ in range(60):
            self.snowflakes.append({
                'x': random.randint(0, 1200),
                'y': random.randint(-50, 800),
                'size': random.randint(2, 5),
                'speed': random.randint(1, 3)
            })
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
        painter.setBrush(QColor(255, 255, 255, 180))
        for flake in self.snowflakes:
            painter.drawEllipse(flake['x'], flake['y'], flake['size'], flake['size'])


#  SIDEBAR BUTTON
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
        self._is_hovering = True;
        self._timer.start();
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovering = False;
        self._timer.stop()
        self.update()
        super().leaveEvent(event)

    def _animate(self):
        if self._is_hovering:
            if self._hover_alpha < 40:
                self._hover_alpha += 5
            else:
                self._timer.stop()
        else:
            if self._hover_alpha > 0:
                self._hover_alpha -= 5
            else:
                self._timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        # Holiday Colors
        if self.isChecked():
            bg_color = QColor("#c0392b")
            text_color = QColor("#f1c40f")
            font_weight = QFont.Weight.Bold
        else:
            bg_color = QColor(255, 255, 255, 15)
            text_color = QColor("#bdc3c7")
            font_weight = QFont.Weight.Normal

        path = QPainterPath();
        path.addRoundedRect(rect, 8, 8)
        painter.fillPath(path, bg_color)

        if self._hover_alpha > 0:
            glow = QLinearGradient(0, 0, rect.width(), 0)
            glow.setColorAt(0.0, QColor(255, 255, 255, self._hover_alpha))
            glow.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.fillPath(path, QBrush(glow))
            if not self.isChecked(): text_color = QColor("white")

        if self.isChecked():
            bar_rect = QRectF(0, 5, 5, rect.height() - 10)
            bar_path = QPainterPath();
            bar_path.addRoundedRect(bar_rect, 2, 2)
            painter.fillPath(bar_path, QColor("#27ae60"))

        painter.setPen(text_color)
        font = self.font();
        font.setPixelSize(13);
        font.setWeight(font_weight);
        painter.setFont(font)
        text_rect = rect.adjusted(15, 0, -5, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())


# BALLOT ANIMATION
class BallotSubmitAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()
        self.paper_y = 0;
        self.paper_alpha = 255
        self.timer = QTimer(self);
        self.timer.timeout.connect(self.animate_step);
        self.timer.setInterval(16)

    def start_animation(self):
        self.paper_y = -150;
        self.paper_alpha = 255;
        self.raise_();
        self.show();
        self.timer.start()

    def stop_animation(self):
        self.timer.stop();
        self.hide()

    def animate_step(self):
        if self.paper_y < 50:
            self.paper_y += 5
        else:
            self.paper_alpha -= 10
            if self.paper_alpha <= 0: self.paper_y = -150; self.paper_alpha = 255
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        cx, cy = self.width() // 2, self.height() // 2

        painter.setPen(QColor("#f1c40f"))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold);
        painter.setFont(font)
        painter.drawText(QRectF(0, cy + 140, self.width(), 50), Qt.AlignmentFlag.AlignCenter, "Submitting Vote... 🎄")

        box_w, box_h = 160, 140;
        slit_y = cy - box_h // 2 + 30

        painter.setBrush(QColor("#c0392b"));
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(cx - box_w // 2 + 10, slit_y, box_w - 20, box_h))

        paper_rect = QRectF(cx - 50, slit_y + self.paper_y, 100, 130)
        painter.save();
        painter.setBrush(QColor(255, 255, 255, self.paper_alpha));
        painter.setPen(QPen(QColor("#bdc3c7"), 2))
        painter.drawRect(paper_rect)
        if self.paper_alpha > 100:
            painter.setPen(QPen(QColor("#27ae60"), 4))
            painter.drawLine(QPointF(cx - 15, slit_y + self.paper_y + 90), QPointF(cx, slit_y + self.paper_y + 105))
            painter.drawLine(QPointF(cx, slit_y + self.paper_y + 105), QPointF(cx + 30, slit_y + self.paper_y + 75))
        painter.restore()

        painter.setBrush(QColor("#27ae60"));
        painter.drawRoundedRect(QRectF(cx - box_w // 2, slit_y, box_w, box_h), 5, 5)
        painter.setBrush(QColor("#f1c40f"));
        painter.drawRoundedRect(QRectF(cx - box_w // 2 - 10, slit_y - 20, box_w + 20, 20), 5, 5)

        painter.setPen(QColor(255, 255, 255, 150))
        painter.drawText(QRectF(cx - box_w // 2, slit_y, box_w, box_h), Qt.AlignmentFlag.AlignCenter, "🎁")


# TIMER WIDGET
class UrgentTimerFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 90)
        self.current_color = QColor("#27ae60")
        self.glow_alpha = 100;
        self.glow_dir = 5
        self.timer = QTimer(self);
        self.timer.timeout.connect(self.animate);
        self.timer.start(50)

        layout = QVBoxLayout(self);
        layout.setSpacing(0);
        layout.setContentsMargins(0, 5, 0, 5)

        self.lbl_title = QLabel("TIME LEFT 🎅")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #27ae60; background: transparent;")

        self.lbl_time = QLabel("--:--")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 32px; font-weight: bold; color: #f1c40f; background: transparent;")

        layout.addWidget(self.lbl_title);
        layout.addWidget(self.lbl_time)

    def update_time(self, text): self.lbl_time.setText(text)

    def set_urgent(self, urgent):
        self.current_color = QColor("#c0392b") if urgent else QColor("#27ae60")
        self.lbl_title.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {self.current_color.name()}; background: transparent;")
        self.timer.setInterval(20 if urgent else 50)

    def animate(self):
        self.glow_alpha += self.glow_dir
        if self.glow_alpha >= 200 or self.glow_alpha <= 50: self.glow_dir *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self);
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect().adjusted(2, 2, -2, -2));
        path = QPainterPath();
        path.addRoundedRect(rect, 15, 15)

        bg_color = QColor(self.current_color);
        bg_color.setAlpha(40)
        painter.fillPath(path, bg_color)

        pen = QPen(
            QColor(self.current_color.red(), self.current_color.green(), self.current_color.blue(), self.glow_alpha))
        pen.setWidth(3);
        painter.setPen(pen);
        painter.drawPath(path)


# RECEIPT DIALOG
class VoteReceiptDialog(QDialog):
    def __init__(self, candidate_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vote Receipt")
        self.setFixedSize(420, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main Background Frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #2ecc71;
                border-radius: 20px;
            }
            QScrollBar:vertical { width: 6px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.3); border-radius: 3px; }
        """)
        layout.addWidget(frame)

        fl = QVBoxLayout(frame)
        fl.setSpacing(15)
        fl.setContentsMargins(25, 30, 25, 30)

        # Success Icon
        icon = QLabel("✅")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 48))
        icon.setStyleSheet("border: none; background: transparent;")
        fl.addWidget(icon)

        # Title
        title = QLabel("VOTE SUBMITTED")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2ecc71; border: none; background: transparent; letter-spacing: 1px;")
        fl.addWidget(title)

        # Instruction Box
        instr_frame = QFrame()
        instr_frame.setStyleSheet("""
            background-color: rgba(241, 196, 15, 0.15); 
            border-radius: 8px; 
            border: 1px dashed #f1c40f;
        """)
        instr_layout = QHBoxLayout(instr_frame)
        instr_layout.setContentsMargins(10, 10, 10, 10)

        instr_lbl = QLabel("📸 Please take a photo of this screen as your receipt before logging out.")
        instr_lbl.setWordWrap(True)
        instr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instr_lbl.setStyleSheet(
            "color: #f1c40f; font-size: 13px; font-weight: 600; border: none; background: transparent;")

        instr_layout.addWidget(instr_lbl)
        fl.addWidget(instr_frame)

        # Candidate List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(container)
        cl.setSpacing(8)

        for pos, name in candidate_list:
            # Item Row
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.08); 
                    border-radius: 10px;
                }
            """)
            rl = QVBoxLayout(row)
            rl.setSpacing(2)
            rl.setContentsMargins(15, 10, 15, 10)

            p_lbl = QLabel(pos)
            p_lbl.setStyleSheet(
                "color: #bdc3c7; font-size: 11px; font-weight: bold; text-transform: uppercase; border: none; background: transparent;")

            n_lbl = QLabel(name)
            n_lbl.setStyleSheet(
                "color: white; font-size: 16px; font-weight: bold; border: none; background: transparent;")

            rl.addWidget(p_lbl)
            rl.addWidget(n_lbl)
            cl.addWidget(row)

        cl.addStretch()
        scroll.setWidget(container)
        fl.addWidget(scroll)

        # Logout Button
        btn = QPushButton("LOGOUT")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                font-weight: bold; 
                font-size: 15px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        btn.clicked.connect(self.accept)
        fl.addWidget(btn)


# CUSTOM POPUP
class CustomPopup(QDialog):
    def __init__(self, parent, title, message, icon_type="info", ok_text="OK", cancel_text="Cancel"):
        super().__init__(parent)
        self.setFixedSize(400, 280)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        color, icon = "#3498db", "⛄"
        if icon_type == "success":
            color, icon = "#27ae60", "🎄"
        elif icon_type == "error":
            color, icon = "#c0392b", "🎅"
        elif icon_type == "warning":
            color, icon = "#f1c40f", "🎁"
        elif icon_type == "question":
            color, icon = "#3498db", "❓"

        layout = QVBoxLayout(self);
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame();
        frame.setStyleSheet(
            f"QFrame {{ background: #0f2027; border-radius: 12px; border: 2px solid {color}; }} QLabel {{ color: white; border: none; }}")
        layout.addWidget(frame)

        fl = QVBoxLayout(frame);
        fl.setContentsMargins(20, 20, 20, 20)

        # Header Layout
        hl = QHBoxLayout();
        il = QLabel(icon);
        il.setFont(QFont("Segoe UI Emoji", 26));
        tl = QLabel(title);
        tl.setFont(QFont("Arial", 16, QFont.Weight.Bold));
        tl.setStyleSheet(f"color: {color};");
        hl.addWidget(il);
        hl.addWidget(tl);
        hl.addStretch();
        fl.addLayout(hl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: rgba(0,0,0,0.2); border-radius: 3px; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.3); border-radius: 3px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        msg_container = QWidget()
        msg_container.setStyleSheet("background: transparent;")
        msg_layout = QVBoxLayout(msg_container)
        msg_layout.setContentsMargins(0, 0, 0, 0)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setFont(QFont("Arial", 11))
        msg.setStyleSheet("color: #ecf0f1;")
        msg.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        msg_layout.addWidget(msg)
        scroll.setWidget(msg_container)

        fl.addWidget(scroll)

        bl = QHBoxLayout();
        bl.addStretch()
        btn_style = f"background: {color}; color: white; font-weight: bold; padding: 6px 20px; border-radius: 6px; border:none;"

        if icon_type == "question":
            y = QPushButton(ok_text);
            y.setCursor(Qt.CursorShape.PointingHandCursor);
            y.setStyleSheet(btn_style);
            y.clicked.connect(self.accept)
            n = QPushButton(cancel_text);
            n.setCursor(Qt.CursorShape.PointingHandCursor);
            n.setStyleSheet("background: #7f8c8d; color: white; padding: 6px 20px; border-radius: 6px; border:none;");
            n.clicked.connect(self.reject)
            bl.addWidget(y);
            bl.addWidget(n)
        else:
            o = QPushButton(ok_text);
            o.setCursor(Qt.CursorShape.PointingHandCursor);
            o.setStyleSheet(btn_style);
            o.clicked.connect(self.accept);
            bl.addWidget(o)
        fl.addLayout(bl);
        self.result_val = True

    @staticmethod
    def show_info(p, t, m, ok="OK"):
        CustomPopup(p, t, m, "success", ok).exec()

    @staticmethod
    def show_error(p, t, m):
        CustomPopup(p, t, m, "error").exec()

    @staticmethod
    def show_warning(p, t, m):
        CustomPopup(p, t, m, "warning").exec()

    @staticmethod
    def ask_question(p, t, m, ok="Yes", no="No"):
        d = CustomPopup(p, t, m, "question", ok, no);
        return d.exec() == QDialog.DialogCode.Accepted


# VOTER DASHBOARD
class VoterDashboard(QMainWindow):
    def __init__(self, db, user_id, session_token):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.session_token = session_token
        self.user_name = self.get_user_name()

        self.selected_candidates = {}
        self.button_groups = {}
        self.clean_exit = False

        self.setup_ui()
        self.setup_timer()
        self.check_voting_status()
        self.load_all_positions()

    def get_user_name(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT full_name FROM users WHERE id=?", (self.user_id,))
            res = cursor.fetchone()
            return res[0] if res else "Student"
        except:
            return "Student"

    # GLOW HELPER
    def apply_glow_effect(self, frame, is_selected):
        shadow = QGraphicsDropShadowEffect(self)
        if is_selected:
            shadow.setBlurRadius(40);
            shadow.setColor(QColor("#27ae60"));
            shadow.setOffset(0, 0)
        else:
            shadow.setBlurRadius(15);
            shadow.setColor(QColor(0, 0, 0, 80));
            shadow.setOffset(3, 3)
        frame.setGraphicsEffect(shadow)

    def check_voting_status(self):
        try:
            if self.db.check_user_voted(self.user_id):
                QTimer.singleShot(100, lambda: self.handle_exit("Already Voted", "You have already cast your vote."))
                return

            status = self.db.get_config('election_status')
            if status != 'active':
                QTimer.singleShot(100, lambda: self.handle_exit("Closed", "The election is currently closed."))
                return
        except Exception as e:
            print(e)

    def handle_exit(self, title, msg):
        CustomPopup.show_error(self, title, msg)
        self.logout(force=True)

    def setup_ui(self):
        self.setWindowTitle("VoteSphere - Voter (Christmas Edition)")
        # WINTER NIGHT BACKGROUND
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f2027, 
                    stop:0.5 #203a43, 
                    stop:1 #2c5364
                );
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # SNOWFALL OVERLAY
        self.snow = SnowFallOverlay(central)
        self.snow.resize(1920, 1080)
        self.snow.lower()

        self.create_sidebar(main_layout)
        self.create_content(main_layout)

        self.submit_animation = BallotSubmitAnimation(central)

    def resizeEvent(self, event):
        self.submit_animation.resize(self.width(), self.height())
        self.snow.resize(self.width(), self.height())
        super().resizeEvent(event)

    def create_sidebar(self, layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame { background-color: rgba(15, 32, 39, 0.95); border-right: 1px solid rgba(255,255,255,0.1); }
            QLabel { color: white; }
        """)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(15, 20, 15, 20)
        sl.setSpacing(15)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            p = QPixmap("logo.png").scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(p)
        except:
            logo.setText("🎄");
            logo.setFont(QFont("Arial", 40))
        sl.addWidget(logo)

        lbl_welcome = QLabel(f"Welcome,\n{self.user_name}")
        lbl_welcome.setWordWrap(True)
        lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_welcome.setStyleSheet("color: #ecf0f1; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        sl.addWidget(lbl_welcome)

        sl.addWidget(QLabel("POSITIONS:"))
        self.scroll_pos = QScrollArea()
        self.scroll_pos.setWidgetResizable(True)
        self.scroll_pos.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.widget_pos = QWidget()
        self.widget_pos.setStyleSheet("background: transparent;")
        self.layout_pos = QVBoxLayout(self.widget_pos)
        self.layout_pos.setSpacing(2)
        self.layout_pos.setContentsMargins(0, 0, 0, 0)
        self.layout_pos.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_pos.setWidget(self.widget_pos)
        sl.addWidget(self.scroll_pos)

        self.lbl_summary = QLabel("0 selected")
        self.lbl_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_summary.setStyleSheet("color: #f1c40f; font-weight: bold; font-size: 12px;")
        sl.addWidget(self.lbl_summary)

        self.btn_submit = QPushButton("SUBMIT VOTE 🎁")
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #f1c40f);
                color: white; border: none; padding: 12px; border-radius: 6px;
                font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background: #e74c3c; margin-top: -2px; }
            QPushButton:disabled { background: #95a5a6; }
        """)
        self.btn_submit.clicked.connect(self.submit_vote)
        sl.addWidget(self.btn_submit)

        btn_logout = QPushButton("LOGOUT")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: rgba(192, 57, 43, 0.2); color: #e74c3c;
                font-weight: bold; border: 1px solid #e74c3c;
                padding: 10px; border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { background: #c0392b; color: white; }
        """)
        btn_logout.clicked.connect(self.logout)
        sl.addWidget(btn_logout)

        layout.addWidget(sidebar)

    def create_content(self, layout):
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(30, 30, 30, 30)

        top_bar = QHBoxLayout();
        title_box = QVBoxLayout()
        header = QLabel("Cast Your Vote ❄️");
        header.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold));
        header.setStyleSheet("color: #f1c40f;")
        sub_header = QLabel("Please select ONE candidate per position below.");
        sub_header.setStyleSheet("color: #bdc3c7; font-size: 16px;")
        title_box.addWidget(header);
        title_box.addWidget(sub_header)
        top_bar.addLayout(title_box);
        top_bar.addStretch()
        self.timer_frame = UrgentTimerFrame();
        top_bar.addWidget(self.timer_frame);
        cl.addLayout(top_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2);
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255,255,255,0.1); }")

        cand_frame = QFrame();
        cand_frame.setStyleSheet("background: transparent;")
        cf_layout = QVBoxLayout(cand_frame);
        cf_layout.setContentsMargins(0, 10, 10, 0)
        self.lbl_current_pos = QLabel("Select Position");
        self.lbl_current_pos.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2ecc71; margin-bottom: 10px; border-left: 5px solid #c0392b; padding-left: 10px;")
        cf_layout.addWidget(self.lbl_current_pos)

        scroll = QScrollArea();
        scroll.setWidgetResizable(True);
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: rgba(0,0,0,0.3); border-radius: 10px; } QScrollBar:vertical { width: 8px; background: rgba(0,0,0,0.2); border-radius: 4px; } QScrollBar::handle:vertical { background: rgba(255,255,255,0.4); border-radius: 4px; }")
        self.widget_cand = QWidget();
        self.widget_cand.setStyleSheet("background: transparent;")
        self.layout_cand = QVBoxLayout(self.widget_cand);
        self.layout_cand.setSpacing(15);
        self.layout_cand.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.widget_cand);
        cf_layout.addWidget(scroll)

        leader_wrapper = QFrame();
        leader_wrapper.setStyleSheet("background: transparent;")
        lw_layout = QVBoxLayout(leader_wrapper);
        lw_layout.setContentsMargins(10, 10, 0, 0)

        lbl_lead = QLabel("LEADING CANDIDATES")
        lbl_lead.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #f1c40f; margin-bottom: 10px; border-left: 5px solid #2ecc71; padding-left: 10px;")
        lw_layout.addWidget(lbl_lead)

        leader_frame = QFrame();
        leader_frame.setMinimumWidth(250);
        leader_frame.setStyleSheet("QFrame { background: rgba(0,0,0,0.3); border-radius: 10px; }")
        lf_layout = QVBoxLayout(leader_frame);
        lf_layout.setContentsMargins(0, 0, 0, 0)

        lead_scroll = QScrollArea();
        lead_scroll.setWidgetResizable(True);
        lead_scroll.setStyleSheet("background: transparent; border: none;")
        self.leaders_widget = QWidget();
        self.leaders_widget.setStyleSheet("background: transparent;")
        self.leaders_layout = QVBoxLayout(self.leaders_widget);
        self.leaders_layout.setSpacing(15);
        self.leaders_layout.setAlignment(Qt.AlignmentFlag.AlignTop);
        self.leaders_layout.setContentsMargins(15, 15, 15, 15)
        lead_scroll.setWidget(self.leaders_widget);
        lf_layout.addWidget(lead_scroll)
        lw_layout.addWidget(leader_frame)

        splitter.addWidget(cand_frame);
        splitter.addWidget(leader_wrapper)
        splitter.setStretchFactor(0, 3);
        splitter.setStretchFactor(1, 1)
        cl.addWidget(splitter);
        layout.addWidget(content)

    def setup_timer(self):
        self.timer = QTimer(self);
        self.timer.timeout.connect(self.update_timer);
        self.timer.start(1000);
        self.update_leaders()

    def load_all_positions(self):
        self.btn_group_pos = QButtonGroup(self);
        self.btn_group_pos.setExclusive(True)
        try:
            cursor = self.db.conn.cursor();
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            positions = [r[0] for r in cursor.fetchall()]
            for i, pos in enumerate(positions):
                btn = GlowPositionButton(pos);
                self.btn_group_pos.addButton(btn)
                btn.clicked.connect(lambda _, p=pos: self.load_candidates(p));
                self.layout_pos.addWidget(btn)
                if i == 0: btn.click()
            self.layout_pos.addStretch()
        except:
            pass

    def update_leaders(self):
        while self.leaders_layout.count():
            item = self.leaders_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        try:
            cursor = self.db.conn.cursor();
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            positions = [r[0] for r in cursor.fetchall()]
            for pos in positions:
                pos_frame = QFrame();
                pos_frame.setStyleSheet(
                    "QFrame { background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }")
                pf_layout = QVBoxLayout(pos_frame);
                pf_layout.setSpacing(5);
                pf_layout.setContentsMargins(10, 8, 10, 8)
                lbl_pos = QLabel(pos.upper());
                lbl_pos.setStyleSheet(
                    "color: #27ae60; font-weight: bold; font-size: 14px; border:none; background:transparent;")
                pf_layout.addWidget(lbl_pos)
                cursor.execute("SELECT name, votes FROM candidates WHERE position=? ORDER BY votes DESC LIMIT 3",
                               (pos,))
                cands = cursor.fetchall()
                if not cands:
                    no_vote = QLabel("No votes.");
                    no_vote.setStyleSheet(
                        "color: #bdc3c7; font-size: 16px; font-style: italic; border:none; background:transparent;")
                    pf_layout.addWidget(no_vote)
                else:
                    for i, (name, votes) in enumerate(cands):
                        row = QHBoxLayout()
                        rank_lbl = QLabel(f"{i + 1}");
                        rank_lbl.setFixedWidth(25);
                        rank_lbl.setStyleSheet(
                            "color: #f1c40f; font-weight: bold; font-size: 16px; border:none; background:transparent;")
                        name_lbl = QLabel(name);
                        name_lbl.setStyleSheet("color: white; font-size: 16px; border:none; background:transparent;")
                        votes_lbl = QLabel(str(votes));
                        votes_lbl.setStyleSheet(
                            "color: #e74c3c; font-weight: bold; font-size: 16px; border:none; background:transparent;")
                        row.addWidget(rank_lbl);
                        row.addWidget(name_lbl, 1);
                        row.addWidget(votes_lbl)
                        pf_layout.addLayout(row)
                self.leaders_layout.addWidget(pos_frame)
        except:
            pass

    def load_candidates(self, position):
        self.lbl_current_pos.setText(position)
        while self.layout_cand.count():
            item = self.layout_cand.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT id, name, grade, image FROM candidates WHERE position=?", (position,))
            candidates = cursor.fetchall()
            if not candidates: self.layout_cand.addWidget(QLabel("No candidates found.")); return
            if position not in self.button_groups: self.button_groups[position] = QButtonGroup(self)
            group = self.button_groups[position]
            for cid, name, grade, img_data in candidates:
                card = QFrame();
                card.setObjectName("candCard");
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                is_selected = (position in self.selected_candidates and self.selected_candidates[position] == cid)
                self.apply_glow_effect(card, is_selected)
                border_col = "#27ae60" if is_selected else "#bdc3c7"
                bg_col = "rgba(39, 174, 96, 0.2)" if is_selected else "rgba(255, 255, 255, 0.1)"
                card.setStyleSheet(
                    f"QFrame#candCard {{ background-color: {bg_col}; border: 2px solid {border_col}; border-radius: 12px; }} QFrame#candCard:hover {{ border: 2px solid #3498db; }}")

                layout = QHBoxLayout(card);
                layout.setContentsMargins(15, 10, 15, 10);
                layout.setSpacing(20)
                rb = QRadioButton();
                rb.setFixedSize(0, 0);
                group.addButton(rb)
                if is_selected: rb.setChecked(True)
                rb.toggled.connect(lambda c, p=position, i=cid, fr=card: self.on_select(c, p, i, fr))
                layout.addWidget(rb)

                def make_clickable(r=rb):
                    r.setChecked(True)

                card.mousePressEvent = lambda e, r=rb: make_clickable(r)

                lbl_img = QLabel();
                lbl_img.setFixedSize(60, 60)
                if img_data:
                    pix = QPixmap();
                    pix.loadFromData(img_data)
                    target = QPixmap(60, 60);
                    target.fill(Qt.GlobalColor.transparent)
                    p = QPainter(target);
                    p.setRenderHint(QPainter.RenderHint.Antialiasing);
                    path = QPainterPath();
                    path.addEllipse(0, 0, 60, 60);
                    p.setClipPath(path);
                    p.drawPixmap(0, 0, pix.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                  Qt.TransformationMode.SmoothTransformation));
                    p.end()
                    lbl_img.setPixmap(target)
                else:
                    lbl_img.setText("❄️");
                    lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter);
                    lbl_img.setStyleSheet("font-size: 24px; background: rgba(255,255,255,0.1); border-radius: 30px;")
                layout.addWidget(lbl_img)

                info = QVBoxLayout();
                info.setSpacing(2)
                l_name = QLabel(name);
                l_name.setStyleSheet(
                    "font-size: 16px; font-weight: bold; color: white; border:none; background: transparent;")
                l_grade = QLabel(grade);
                l_grade.setStyleSheet("font-size: 13px; color: #bdc3c7; border:none; background: transparent;")
                info.addWidget(l_name);
                info.addWidget(l_grade)
                layout.addLayout(info);
                layout.addStretch()

                if is_selected:
                    lbl_check = QLabel("🎄");
                    lbl_check.setStyleSheet("font-size: 20px; border:none; background: transparent;")
                    layout.addWidget(lbl_check)
                self.layout_cand.addWidget(card)
        except:
            pass

    def on_select(self, checked, pos, cid, frame):
        if checked:
            self.selected_candidates[pos] = cid;
            self.update_summary();
            self.load_candidates(pos)

    def update_summary(self):
        count = len(self.selected_candidates)
        self.lbl_summary.setText(f"{count} Position(s) Selected")
        self.btn_submit.setText(f"SUBMIT ({count})")

    def update_timer(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT session_token FROM users WHERE id=?", (self.user_id,))
            res = cursor.fetchone()
            if not res or res[0] != self.session_token:
                self.timer.stop();
                CustomPopup.show_error(self, "Session Expired", "Logged in elsewhere.");
                self.logout(force=True);
                return
            cursor.execute("UPDATE users SET last_active=CURRENT_TIMESTAMP WHERE id=?", (self.user_id,));
            self.db.conn.commit()

            self.update_leaders()

            status = self.db.get_config('election_status')
            if status != 'active': self.timer.stop(); self.handle_exit("Closed", "Election Ended."); return

            target = self.db.get_config('election_target_time')
            if not target: return

            left = QDateTime.currentDateTime().secsTo(QDateTime.fromString(target, Qt.DateFormat.ISODate))
            if left <= 0:
                self.timer.stop();
                self.handle_exit("Time's Up", "Election Ended.")
            else:
                h = left // 3600;
                m = (left % 3600) // 60;
                s = left % 60
                self.timer_frame.update_time(f"{h:02}:{m:02}:{s:02}")
                self.timer_frame.set_urgent(left <= 600)
        except Exception as e:
            print(f"Timer Loop Error: {e}")

    def submit_vote(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT DISTINCT position FROM candidates ORDER BY position")
            all_positions = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return

        missing_positions = [pos for pos in all_positions if pos not in self.selected_candidates]

        if missing_positions:
            missing_str = "\n".join([f"• {pos}" for pos in missing_positions])
            CustomPopup.show_warning(self, "Incomplete Ballot",
                                     f"You cannot submit yet!\n\nPlease select a candidate for the following positions:\n{missing_str}")
            return

        # Confirmation Dialog
        msg = "Are you sure you want to submit your votes?\n\nClick 'Review' to change candidates.\nClick 'Submit' to proceed."
        if CustomPopup.ask_question(self, "Review Selection", msg, ok="Submit", no="Review"):
            self.clean_exit = True
            self.submit_animation.start_animation()
            QTimer.singleShot(2500, self.finalize)

    def finalize(self):
        try:
            c = self.db.conn.cursor();
            receipt_list = []
            for p, id in self.selected_candidates.items():
                c.execute("INSERT INTO votes (voter_id, candidate_id, position) VALUES (?,?,?)", (self.user_id, id, p))
                c.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (id,))
                c.execute("SELECT name FROM candidates WHERE id=?", (id,));
                n = c.fetchone()[0]
                receipt_list.append((p, n))

            c.execute("UPDATE users SET voted=1 WHERE id=?", (self.user_id,));

            # AUDIT LOGGING
            if hasattr(self.db, 'log_audit'):
                self.db.log_audit(self.user_name, "Submitted Vote")

            self.db.conn.commit()

            self.submit_animation.stop_animation()
            VoteReceiptDialog(receipt_list, self).exec()
            self.logout(force=True)
        except Exception as e:
            self.submit_animation.stop_animation();
            print(e)

    # INTERCEPT CLOSE EVENT
    def closeEvent(self, event):
        if self.clean_exit:
            event.accept()
            return

        if CustomPopup.ask_question(self, "Confirm Exit", "Do you really want to log out?"):
            self.timer.stop()
            try:
                self.db.conn.execute("UPDATE users SET last_active = NULL WHERE id=?", (self.user_id,))
                self.db.conn.commit()
            except:
                pass

            from view.common.login_window import LoginWindow
            self.win = LoginWindow()
            self.win.show()
            event.accept()
        else:
            event.ignore()

    def logout(self, force=False):
        if force or CustomPopup.ask_question(self, "Logout", "Are you sure?"):
            self.clean_exit = True
            self.timer.stop()
            try:
                self.db.conn.execute("UPDATE users SET last_active = NULL WHERE id=?",
                                     (self.user_id,));
                self.db.conn.commit()
            except:
                pass
            from view.common.login_window import LoginWindow
            self.win = LoginWindow();
            self.win.show();
            self.close()