import sys
import traceback
import requests
import webbrowser
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from models.database import Database
from controllers.login_controller import LoginController

APP_VERSION = "2.3"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Zento-0616/VoteSphere-Distribution/refs/heads/main/version.txt"
GITHUB_DOWNLOAD_URL = "https://github.com/Zento-0616/VoteSphere-Distribution/releases/latest"


def check_for_updates():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest = response.text.strip()
            if float(latest) > float(APP_VERSION):
                msg = QMessageBox()
                msg.setText(f"Update available: {latest}")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    webbrowser.open(GITHUB_DOWNLOAD_URL)
                    sys.exit()
    except:
        pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VoteSphere")

    try:
        check_for_updates()
        db = Database()
        if not db.is_version_valid(APP_VERSION):
            sys.exit()

        global controller
        controller = LoginController(db)

        sys.exit(app.exec())
    except Exception as e:
        error_details = traceback.format_exc()
        error_msg = QMessageBox()
        error_msg.setText(f"Fatal Error: {str(e)}\n\n{error_details}")
        error_msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()