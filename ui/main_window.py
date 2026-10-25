from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
)

from PySide6.QtCore import Qt

from ui.billing_page import BillingPage
from ui.dashboard_page import DashboardPage
from ui.settings_page import SettingsPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Billing_System")
        self.resize(1250, 800)

        self.setMinimumSize(1000, 650)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------- SIDEBAR ----------------

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(12)

        logo_title = QLabel("Billing_system")
        logo_title.setObjectName("brand")

        subtitle = QLabel("Sales & Service")
        subtitle.setObjectName("brand_subtitle")

        sidebar_layout.addWidget(logo_title)
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(30)

        self.billing_btn = QPushButton("  Billing")
        self.dashboard_btn = QPushButton("  Dashboard & Sales")
        self.settings_btn = QPushButton("  Settings")

        for button in (
            self.billing_btn,
            self.dashboard_btn,
            self.settings_btn,
        ):
            button.setObjectName("nav_button")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        footer = QLabel("Offline Desktop Application")
        footer.setObjectName("sidebar_footer")

        sidebar_layout.addWidget(footer)

        # ---------------- CONTENT ----------------

        self.stack = QStackedWidget()

        self.billing_page = BillingPage()
        self.dashboard_page = DashboardPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.billing_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.settings_page)

        # ---------------- NAVIGATION ----------------

        self.billing_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.dashboard_btn.clicked.connect(
            self.show_dashboard
        )

        self.settings_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(2)
        )

        # ---------------- LAYOUT ----------------

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, 1)

        # Refresh dashboard whenever it is opened.
        self.dashboard_page.setObjectName("dashboard_page")

        self.apply_styles()

    def show_dashboard(self):
        self.dashboard_page.refresh_data()
        self.stack.setCurrentIndex(1)

    def apply_styles(self): 
        self.setStyleSheet("""
        QWidget {
            font-family: Arial;
            font-size: 13px;
            color: #212529;
        }

        QMainWindow {
            background-color: #f5f7fa;
        }

        QLabel {
            color: #212529;
            background-color: transparent;
        }

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #ced4da;
            border-radius: 5px;
            padding: 6px;
        }

        QTableWidget {
            background-color: #ffffff;
            color: #212529;
            gridline-color: #dee2e6;
            selection-background-color: #cfe2ff;
            selection-color: #212529;
            alternate-background-color: #f8f9fa;
        }

        QHeaderView::section {
            background-color: #e9ecef;
            color: #212529;
            padding: 8px;
            border: 1px solid #dee2e6;
            font-weight: bold;
        }

        QPushButton {
            background-color: #0d6efd;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            padding: 8px 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #0b5ed7;
        }

        QPushButton:disabled {
            background-color: #adb5bd;
            color: #ffffff;
        }

        QGroupBox {
            color: #212529;
            font-weight: bold;
            border: 1px solid #ced4da;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)