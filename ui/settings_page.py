from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)

from database.db import get_setting, save_setting


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        root.addWidget(title)

        form = QFormLayout()

        self.shop_name = QLineEdit(
            get_setting("shop_name")
        )

        self.tagline = QLineEdit(
            get_setting("tagline")
        )

        self.address = QLineEdit(
            get_setting("address")
        )

        self.phone = QLineEdit(
            get_setting("phone")
        )

        self.email = QLineEdit(
            get_setting("email")
        )

        self.invoice_prefix = QLineEdit(
            get_setting("invoice_prefix", "INV")
        )

        self.tax_rate = QLineEdit(
            get_setting("default_tax_rate", "0")
        )

        self.logo_path = QLineEdit(
            get_setting("logo_path")
        )

        self.logo_path.setReadOnly(True)

        self.choose_logo_button = QPushButton(
            "Choose Logo"
        )

        logo_layout = QVBoxLayout()

        logo_layout.addWidget(self.logo_path)
        logo_layout.addWidget(self.choose_logo_button)

        form.addRow("Shop Name:", self.shop_name)
        form.addRow("Tagline:", self.tagline)
        form.addRow("Address:", self.address)
        form.addRow("Phone:", self.phone)
        form.addRow("Email:", self.email)
        form.addRow("Invoice Prefix:", self.invoice_prefix)
        form.addRow("Default Tax Rate (%):", self.tax_rate)
        form.addRow("Shop Logo:", logo_layout)

        root.addLayout(form)

        self.save_button = QPushButton(
            "Save Settings"
        )

        root.addWidget(self.save_button)

        root.addStretch()

        self.choose_logo_button.clicked.connect(
            self.choose_logo
        )

        self.save_button.clicked.connect(
            self.save_settings
        )

    def choose_logo(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Shop Logo",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )

        if path:
            self.logo_path.setText(path)

    def save_settings(self):

        try:

            tax_rate = float(
                self.tax_rate.text().strip()
            )

            if not 0 <= tax_rate <= 100:
                raise ValueError(
                    "Tax rate must be between 0 and 100."
                )

            prefix = self.invoice_prefix.text().strip()

            if not prefix:
                raise ValueError(
                    "Invoice prefix cannot be empty."
                )

            if not self.shop_name.text().strip():
                raise ValueError(
                    "Shop name cannot be empty."
                )

            if (
                self.logo_path.text()
                and not Path(self.logo_path.text()).is_file()
            ):
                raise ValueError(
                    "The selected logo file does not exist."
                )

            settings = {
                "shop_name": self.shop_name.text().strip(),
                "tagline": self.tagline.text().strip(),
                "address": self.address.text().strip(),
                "phone": self.phone.text().strip(),
                "email": self.email.text().strip(),
                "invoice_prefix": prefix,
                "default_tax_rate": str(tax_rate),
                "logo_path": self.logo_path.text().strip(),
            }

            for key, value in settings.items():
                save_setting(key, value)

            QMessageBox.information(
                self,
                "Settings Saved",
                "Your shop settings have been saved."
            )

        except ValueError as exc:

            QMessageBox.warning(
                self,
                "Invalid Settings",
                str(exc)
            )