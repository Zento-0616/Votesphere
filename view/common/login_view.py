import os
import sys
import random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace("\\", "/")


class LoadingScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(15)
        QTimer.singleShot(2000, self.accept)

    def rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(15, 23, 42, 230))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(50, 50, 200, 200)
        pen = QPen()
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(QColor(255, 255, 255, 30))
        painter.setPen(pen)
        painter.drawEllipse(70, 70, 160, 160)
        pen.setColor(QColor("#3498db"))
        painter.setPen(pen)
        painter.drawArc(70, 70, 160, 160, -self.angle * 16, 120 * 16)
        painter.setPen(QColor("#ecf0f1"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "LOADING...")


class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.eye_btn = QToolButton(self)
        self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.setText("👁️")
        self.eye_btn.setStyleSheet("""
            QToolButton { border: none; background: transparent; color: #bdc3c7; font-size: 16px; }
            QToolButton:hover { color: #3498db; }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(self.eye_btn)
        self.eye_btn.pressed.connect(lambda: self.setEchoMode(QLineEdit.EchoMode.Normal))
        self.eye_btn.released.connect(lambda: self.setEchoMode(QLineEdit.EchoMode.Password))


class ChristmasSnakeFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(480)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(20)

    def animate(self):
        self.angle -= 2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect().adjusted(4, 4, -4, -4))
        path = QPainterPath()
        path.addRoundedRect(rect, 25, 25)
        painter.fillPath(path, QColor(25, 35, 45, 230))
        pen = QPen()
        pen.setWidth(4)
        gradient = QConicalGradient(rect.center(), self.angle)
        gradient.setColorAt(0.0, QColor("#3498db"))
        gradient.setColorAt(0.5, QColor("#2ecc71"))
        gradient.setColorAt(1.0, QColor("#3498db"))
        pen.setBrush(QBrush(gradient))
        painter.setPen(pen)
        painter.drawPath(path)


class SnowFallBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.snowflakes = [{'x': random.randint(0, 1920), 'y': random.randint(-50, 1080), 'size': random.randint(1, 3),
                            'speed': random.uniform(0.5, 1.5)} for _ in range(80)]
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


class CustomPopup(QDialog):
    def __init__(self, parent, title, message, icon_type="info"):
        super().__init__(parent)
        self.setFixedSize(420, 200)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        color = "#2ecc71" if icon_type == "success" else "#e74c3c" if icon_type == "error" else "#3498db"

        layout = QVBoxLayout(self)
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background: #1a1a1a; border: 2px solid {color}; border-radius: 12px; }}")
        layout.addWidget(frame)

        fl = QVBoxLayout(frame)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px; border: none;")
        lbl_m = QLabel(message)
        lbl_m.setStyleSheet("color: white; border: none;")
        lbl_m.setWordWrap(True)

        fl.addWidget(lbl_t)
        fl.addWidget(lbl_m)
        btn = QPushButton("Continue")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet(f"background: {color}; color: white; font-weight: bold; border-radius: 6px; padding: 10px;")
        fl.addWidget(btn)

    @staticmethod
    def show_error(p, t, m): CustomPopup(p, t, m, "error").exec()

    @staticmethod
    def show_warning(p, t, m): CustomPopup(p, t, m, "warning").exec()

    @staticmethod
    def show_info(p, t, m): CustomPopup(p, t, m, "success").exec()


class LoginView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.showMaximized()

    def setup_ui(self):
        self.setWindowTitle("VoteSphere - Secure Portal")
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

        bg_path = resource_path("background2.png")
        if os.path.exists(bg_path):
            self.setStyleSheet(
                f"QMainWindow {{ border-image: url({bg_path.replace('\\', '/')}) 0 0 0 0 stretch stretch; }}")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.snow = SnowFallBackground(central)

        self.card = ChristmasSnakeFrame()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(45, 50, 45, 50)
        card_layout.setSpacing(10)

        # 1. Logo
        logo_label = QLabel()
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            logo_label.setPixmap(QPixmap(logo_path).scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio,
                                                           Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("🗳️")
            logo_label.setStyleSheet("color: #3498db; font-size: 70px; border: none; background: transparent;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo_label)

        # 2. Titles
        card_layout.addWidget(QLabel("VOTESPHERE", alignment=Qt.AlignmentFlag.AlignCenter,
                                     styleSheet="color: white; font-size: 26px; font-weight: bold; letter-spacing: 3px; border: none; background: transparent;"))
        card_layout.addWidget(QLabel("Secure Login Access", alignment=Qt.AlignmentFlag.AlignCenter,
                                     styleSheet="color: #94a3b8; font-size: 16px; border: none; background: transparent;"))

        card_layout.addSpacing(15)

        # Styles
        input_style = """
            QLineEdit { 
                padding: 12px; 
                border-radius: 8px; 
                background: rgba(15, 23, 42, 0.6); 
                color: white; 
                font-size: 15px; 
                border: 1px solid rgba(255, 255, 255, 0.1); 
            } 
            QLineEdit:focus { border: 2px solid #3498db; }
        """
        label_style = "color: #64748b; font-weight: bold; font-size: 11px; border: none; background: transparent;"

        # 3. Username Field
        card_layout.addWidget(QLabel("STUDENT ID", styleSheet=label_style))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your credentials")
        self.username_input.setStyleSheet(input_style)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(10)

        # 4. Password Field
        card_layout.addWidget(QLabel("PASSWORD", styleSheet=label_style))
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setStyleSheet(input_style)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(25)

        # 5. Sign In Button
        self.login_btn = QPushButton("SIGN IN")
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db); 
                color: white; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 16px; 
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #5dade2);
            }
        """)
        card_layout.addWidget(self.login_btn)

        main_layout.addWidget(self.card)

    def resizeEvent(self, event):
        if hasattr(self, 'snow'):
            self.snow.resize(self.width(), self.height())
        super().resizeEvent(event)

    def get_credentials(self):
        return self.username_input.text().strip(), self.password_input.text().strip()

    def show_loading(self):
        LoadingScreen(self).exec()