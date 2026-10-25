import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from database.db import initialize_database
from ui.main_window import MainWindow


def main():

    app = QApplication(sys.argv)

    app.setApplicationName("SmartShop POS")

    try:

        initialize_database()

        window = MainWindow()

        window.show()

        sys.exit(app.exec())

    except Exception as exc:

        QMessageBox.critical(
            None,
            "Application Error",
            str(exc)
        )

        raise


if __name__ == "__main__":
    main()