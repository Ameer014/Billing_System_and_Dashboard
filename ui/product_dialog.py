from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
)

from database.db import get_connection


class ProductDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New Product")
        self.setMinimumWidth(420)

        root = QVBoxLayout(self)
        form = QFormLayout()

        # Product details
        self.product_code = QLineEdit()
        self.product_name = QLineEdit()
        self.category = QLineEdit()
        self.brand = QLineEdit()

        # Purchase price
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 100000000)
        self.purchase_price.setDecimals(2)
        self.purchase_price.setPrefix("₹ ")

        # Selling price
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 100000000)
        self.selling_price.setDecimals(2)
        self.selling_price.setPrefix("₹ ")

        # Stock quantity
        self.stock_quantity = QSpinBox()
        self.stock_quantity.setRange(0, 10000000)

        # Reorder level
        self.reorder_level = QSpinBox()
        self.reorder_level.setRange(0, 10000000)
        self.reorder_level.setValue(5)

        form.addRow("Product Code:", self.product_code)
        form.addRow("Product Name:", self.product_name)
        form.addRow("Category:", self.category)
        form.addRow("Brand:", self.brand)
        form.addRow("Purchase Price:", self.purchase_price)
        form.addRow("Selling Price:", self.selling_price)
        form.addRow("Stock Quantity:", self.stock_quantity)
        form.addRow("Reorder Level:", self.reorder_level)

        root.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Product")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        root.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_product)
        self.cancel_button.clicked.connect(self.reject)

    def save_product(self):

        code = self.product_code.text().strip()
        name = self.product_name.text().strip()
        category = self.category.text().strip()
        brand = self.brand.text().strip()

        purchase_price = self.purchase_price.value()
        selling_price = self.selling_price.value()
        stock = self.stock_quantity.value()
        reorder_level = self.reorder_level.value()

        # Validate required fields
        if not code:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a product code."
            )
            self.product_code.setFocus()
            return

        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a product name."
            )
            self.product_name.setFocus()
            return

        if selling_price <= 0:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Selling price must be greater than zero."
            )
            self.selling_price.setFocus()
            return

        if purchase_price > selling_price:
            reply = QMessageBox.question(
                self,
                "Check Prices",
                "Purchase price exceeds selling price. Save anyway?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        try:

            with get_connection() as conn:

                conn.execute(
                    """
                    INSERT INTO products (
                        product_code,
                        product_name,
                        category,
                        brand,
                        purchase_price,
                        selling_price,
                        stock_quantity,
                        reorder_level
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        code,
                        name,
                        category,
                        brand,
                        purchase_price,
                        selling_price,
                        stock,
                        reorder_level
                    )
                )

                product_id = conn.execute(
                    """
                    SELECT id
                    FROM products
                    WHERE product_code = ?
                    """,
                    (code,)
                ).fetchone()["id"]

                if stock > 0:

                    conn.execute(
                        """
                        INSERT INTO stock_movements (
                            product_id,
                            movement_type,
                            quantity,
                            reference
                        )
                        VALUES (?, 'OPENING_STOCK', ?, ?)
                        """,
                        (
                            product_id,
                            stock,
                            "Initial product entry"
                        )
                    )

            QMessageBox.information(
                self,
                "Success",
                f"Product '{name}' added successfully."
            )

            self.accept()

        except Exception as exc:

            error_message = str(exc)

            if "UNIQUE constraint failed" in error_message:
                error_message = (
                    "This product code already exists. "
                    "Please enter a unique product code."
                )

            QMessageBox.critical(
                self,
                "Unable to Save Product",
                error_message
            )