import sys
import traceback  # Added this to see line numbers
from PyQt6.QtWidgets import QApplication, QMessageBox
from view.common.login_window import LoginWindow


def main():
    try:
        app = QApplication(sys.argv)

        app.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
            QWidget {
                font-family: Arial, sans-serif;
            }
        """)

        login_window = LoginWindow()
        login_window.show()

        sys.exit(app.exec())

    except Exception as e:
        print("--- FULL ERROR TRACEBACK ---")
        traceback.print_exc()
        print("----------------------------")

        if not QApplication.instance():
            app = QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal Error", f"The application encountered an error:\n{str(e)}")


if __name__ == "__main__":
    main()