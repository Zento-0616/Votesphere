from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QLineEdit, QDialog,
                             QGraphicsOpacityEffect, QSizePolicy, QToolButton)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRegularExpression, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QFont, QPixmap, QRegularExpressionValidator, QPainter,
                         QColor, QPen, QConicalGradient, QBrush, QPainterPath, QLinearGradient)
import uuid
import random
from datetime import datetime, timedelta

from models.database import Database
from view.admin.admin_dashboard import AdminDashboard
from view.voter.voter_dashboard import VoterDashboard


class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)

        self.eye_btn = QToolButton(self)
        self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.setText("👁️")
        self.eye_btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                color: #bdc3c7;
                font-size: 16px;
                padding: 0px;
            }
            QToolButton:pressed {
                color: #2ecc71;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(self.eye_btn)

        self.eye_btn.pressed.connect(self.show_password)
        self.eye_btn.released.connect(self.hide_password)

    def show_password(self):
        self.setEchoMode(QLineEdit.EchoMode.Normal)

    def hide_password(self):
        self.setEchoMode(QLineEdit.EchoMode.Password)


# CHRISTMAS SNAKE BORDER
class ChristmasSnakeFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(480)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)

    def animate(self):
        self.angle -= 4
        if self.angle < 0: self.angle = 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect().adjusted(4, 4, -4, -4))
        path = QPainterPath()
        path.addRoundedRect(rect, 25, 25)

        painter.fillPath(path, QColor(0, 0, 0, 200))

        pen = QPen()
        pen.setWidth(5)
        gradient = QConicalGradient(rect.center(), self.angle)

        gradient.setColorAt(0.0, QColor("#ff0000"))
        gradient.setColorAt(0.25, QColor("#ffffff"))
        gradient.setColorAt(0.5, QColor("#00ff00"))
        gradient.setColorAt(0.75, QColor("#ffffff"))
        gradient.setColorAt(1.0, QColor("#ff0000"))

        pen.setBrush(QBrush(gradient))
        painter.setPen(pen)
        painter.drawPath(path)


# SNOWFALL ANIMATION
class SnowFallBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.snowflakes = []
        for _ in range(150):
            self.snowflakes.append({
                'x': random.randint(0, 1920),
                'y': random.randint(-50, 1080),
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
        painter.setBrush(QColor(255, 255, 255, 200))

        for flake in self.snowflakes:
            painter.drawEllipse(flake['x'], flake['y'], flake['size'], flake['size'])


class CustomPopup(QDialog):
    def __init__(self, parent, title, message, icon_type="info"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if icon_type == "success":
            self.icon_text = "🎄"
            self.accent_color = "#27ae60"
        elif icon_type == "error":
            self.icon_text = "🎅"
            self.accent_color = "#e74c3c"
        elif icon_type == "warning":
            self.icon_text = "🎁"
            self.accent_color = "#f1c40f"
        else:
            self.icon_text = "⛄"
            self.accent_color = "#3498db"

        self.setup_ui(title, message)

    def setup_ui(self, title, message):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3e50;
                border: 2px solid {self.accent_color};
                border-radius: 15px;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: #ecf0f1;
            }}
        """)
        layout.addWidget(self.frame)

        content = QVBoxLayout(self.frame)
        content.setContentsMargins(25, 25, 25, 25)
        content.setSpacing(10)

        header = QHBoxLayout()
        icon = QLabel(self.icon_text)
        icon.setFont(QFont("Segoe UI Emoji", 32))
        header.addWidget(icon)

        tl = QLabel(title)
        tl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        tl.setStyleSheet(f"color: {self.accent_color}; border: none;")
        header.addWidget(tl)
        header.addStretch()
        content.addLayout(header)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 12))
        msg.setStyleSheet("color: #ecf0f1; border: none; padding-left: 5px;")
        content.addWidget(msg)

        content.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setFixedSize(100, 35)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white; 
                font-weight: bold; 
                border-radius: 8px; 
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                color: {self.accent_color}; 
                border: 1px solid {self.accent_color};
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        content.addLayout(btn_layout)

    @staticmethod
    def show_error(p, t, m):
        CustomPopup(p, t, m, "error").exec()

    @staticmethod
    def show_warning(p, t, m):
        CustomPopup(p, t, m, "warning").exec()

    @staticmethod
    def show_info(p, t, m):
        CustomPopup(p, t, m, "success").exec()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()


        self.setup_ui()
        self.fade_animation()
        self.showMaximized()

    def setup_ui(self):
        self.setWindowTitle("VoteSphere - Christmas Edition")
        self.setStyleSheet("QMainWindow { border-image: url(background2.png) 0 0 0 0 stretch stretch; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.snow = SnowFallBackground(central_widget)
        self.snow.resize(1920, 1080)
        self.snow.lower()

        card = ChristmasSnakeFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 50, 40, 50)
        card_layout.setSpacing(10)

        logo_label = QLabel()
        logo_label.setStyleSheet("background: transparent; border: none;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            logo_pixmap = QPixmap("logo.png").scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("🎄🗳️🎄")
            logo_label.setFont(QFont("Segoe UI Emoji", 80))
            logo_label.setStyleSheet("color: white; background: transparent; border: none;")

        card_layout.addWidget(logo_label)
        card_layout.addSpacing(10)

        welcome_label = QLabel("MERRY CHRISTMAS")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #f1c40f; background: transparent; border: none; letter-spacing: 2px;")
        card_layout.addWidget(welcome_label)

        sub_label = QLabel("Welcome")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("color: #ecf0f1; font-size: 20px; margin-bottom: 10px;")
        card_layout.addWidget(sub_label)

        input_style = """
            QLineEdit {
                padding: 12px;
                padding-right: 35px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.1);
                color: white; 
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
                background: rgba(255,255,255,0.2);
            }
            QLabel { color: #bdc3c7; font-weight: bold; }
        """

        id_label = QLabel("Student ID:")
        id_label.setStyleSheet("color: #bdc3c7; font-weight: bold;")
        card_layout.addWidget(id_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter ID ❄️")
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet(input_style)

        regex = QRegularExpression("[a-zA-Z0-9]*")
        self.username_input.setValidator(QRegularExpressionValidator(regex))
        self.username_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(10)

        pass_label = QLabel("Password:")
        pass_label.setStyleSheet("color: #bdc3c7; font-weight: bold;")
        card_layout.addWidget(pass_label)

        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("Enter Password 🔑")
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(25)

        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #f1c40f);
                color: white; border-radius: 12px; font-weight: bold; font-size: 18px;
                border: 2px solid rgba(255,255,255,0.2); letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #f39c12);
                margin-top: 2px;
            }
            QPushButton:pressed { margin-top: 4px; border: none; }
            QPushButton:disabled { background: #7f8c8d; color: #bdc3c7; border: 1px solid #95a5a6; }
        """)
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setDefault(True)
        card_layout.addWidget(self.login_btn)

        main_layout.addWidget(card)

    def resizeEvent(self, event):
        self.snow.resize(self.width(), self.height())
        super().resizeEvent(event)

    def fade_animation(self):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def login(self):
        self.login_btn.setEnabled(False)
        self.login_btn.repaint()

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            CustomPopup.show_warning(self, "Missing Input", "Please enter both username and password.")
            self.login_btn.setEnabled(True)
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT value FROM system_config WHERE key='election_status'")
            row = cursor.fetchone()
            status = row[0] if row else 'inactive'

            cursor.execute(
                "SELECT id, username, password, role, last_active FROM users WHERE username=? AND password=?",
                (username, password))
            user = cursor.fetchone()

            if user:
                user_id, username, password, role, last_active_str = user

                if role == "voter" and last_active_str:
                    try:
                        last_active = datetime.strptime(last_active_str, '%Y-%m-%d %H:%M:%S')
                        if datetime.utcnow() - last_active < timedelta(seconds=15):
                            CustomPopup.show_error(self, "Access Denied",
                                                   "Account active on another device.\nPlease wait 15 seconds.")
                            self.login_btn.setEnabled(True)
                            return
                    except:
                        pass

                token = str(uuid.uuid4())
                cursor.execute("UPDATE users SET session_token=?, last_active=CURRENT_TIMESTAMP WHERE id=?",
                               (token, user_id))
                self.db.conn.commit()

                if role == "voter":
                    if status != 'active':
                        CustomPopup.show_error(self, "Election Closed", "Election is closed.")
                        self.login_btn.setEnabled(True)
                        return
                    if self.db.check_user_voted(user_id):
                        CustomPopup.show_info(self, "Already Voted", "You have already voted.")
                        self.login_btn.setEnabled(True)
                        return
                    self.dash = VoterDashboard(self.db, user_id, token)
                    self.dash.showMaximized()
                elif role == "admin":
                    self.dash = AdminDashboard(self.db, user_id)
                    self.dash.showMaximized()

                self.hide()
            else:
                CustomPopup.show_error(self, "Login Failed", "Invalid credentials.")
                self.login_btn.setEnabled(True)
        except Exception as e:
            CustomPopup.show_error(self, "System Error", str(e))
            self.login_btn.setEnabled(True)