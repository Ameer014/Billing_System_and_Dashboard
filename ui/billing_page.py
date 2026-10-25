from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,   
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
)
from ui.product_dialog import ProductDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from pathlib import Path

from services.billing_service import (
    get_products,
    save_sale,
)

from services.invoice_service import generate_invoice


class BillingPage(QWidget):

    def __init__(self):
        super().__init__()

        self.cart = []

        root = QVBoxLayout(self)

        title = QLabel("Billing")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        root.addWidget(title)

        # ---------------- CUSTOMER DETAILS ----------------

        customer_form = QFormLayout()

        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_address = QLineEdit()

        self.customer_name.setPlaceholderText(
            "Customer name or leave blank for walk-in"
        )

        self.customer_phone.setPlaceholderText(
            "Mobile number (optional)"
        )

        self.customer_address.setPlaceholderText(
            "Address (optional)"
        )

        customer_form.addRow(
            "Customer Name:",
            self.customer_name
        )

        customer_form.addRow(
            "Mobile Number:",
            self.customer_phone
        )

        customer_form.addRow(
            "Address:",
            self.customer_address
        )

        root.addLayout(customer_form)

        # ---------------- AVAILABLE PRODUCTS ----------------

        available_header = QHBoxLayout()
        available_title = QLabel("Available Products")
        available_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.new_product_button = QPushButton("+ Add New Product")
        available_header.addWidget(available_title)
        available_header.addStretch()
        available_header.addWidget(self.new_product_button)
        root.addLayout(available_header)

        # Search controls stay with the available-products list.
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search available products by name..."
        )

        self.search_button = QPushButton("Search")

        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.search_button)
        root.addLayout(search_layout)

        self.product_table = QTableWidget(0, 6)
        self.product_table.setHorizontalHeaderLabels([
            "ID",
            "Product",
            "Price",
            "Available Stock",
            "+",
            "-"
        ])
        self.product_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.product_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.product_table.setColumnHidden(0, True)
        self.product_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )
        root.addWidget(self.product_table, 2)

        # ---------------- CURRENT BILL ----------------

        cart_header = QHBoxLayout()
        cart_title = QLabel("Current Bill")
        cart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        cart_header.addWidget(cart_title)
        cart_header.addStretch()

        root.addLayout(cart_header)

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels([
            "Product ID",
            "Product",
            "Quantity",
            "Unit Price",
            "Amount"
        ])
        self.cart_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.cart_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.cart_table.setColumnHidden(0, True)
        self.cart_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )
        root.addWidget(self.cart_table, 2)

        # ---------------- TOTALS ----------------

        totals_layout = QHBoxLayout()

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(1_000_000)
        self.discount_input.setDecimals(2)
        self.discount_input.setPrefix("₹ ")

        self.tax_label = QLabel("Tax: ₹ 0.00")

        self.total_label = QLabel("Total: ₹ 0.00")
        self.total_label.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        self.payment_method = QComboBox()

        self.payment_method.addItems([
            "Cash",
            "UPI",
            "Card",
            "Bank Transfer"
        ])

        totals_layout.addWidget(QLabel("Discount:"))
        totals_layout.addWidget(self.discount_input)
        totals_layout.addWidget(self.tax_label)
        totals_layout.addWidget(self.payment_method)
        totals_layout.addWidget(self.total_label)

        root.addLayout(totals_layout)

        # ---------------- ACTIONS ----------------

        actions = QHBoxLayout()

        self.clear_button = QPushButton("Clear Bill")
        self.complete_button = QPushButton("Complete Sale")
        self.invoice_button = QPushButton("Generate A4 Invoice")

        actions.addWidget(self.clear_button)
        actions.addWidget(self.complete_button)
        actions.addWidget(self.invoice_button)

        root.addLayout(actions)

        # ---------------- SIGNALS ----------------

        self.search_button.clicked.connect(
            self.load_products
        )

        self.search_input.returnPressed.connect(
            self.load_products
        )

        self.discount_input.valueChanged.connect(
            self.update_totals
        )

        self.clear_button.clicked.connect(
            self.clear_bill
        )

        self.complete_button.clicked.connect(
            self.complete_sale
        )

        self.invoice_button.clicked.connect(
            self.open_invoice
        )
        self.new_product_button.clicked.connect(
           self.add_new_product
        )
        self.search_input.textChanged.connect(
            self.load_products
        )       

        self.last_invoice = None

        self.load_products()
        self.refresh_cart()

    def load_products(self):
        search = self.search_input.text().strip()
        products = get_products(search)

        self.product_table.setRowCount(0)

        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)

            values = [
                product["id"],
                product["product_name"],
                f"₹ {product['selling_price']:.2f}",
                product["stock_quantity"],
                "",
                ""
            ]

            for col, value in enumerate(values[:4]):
                item = QTableWidgetItem(str(value))
                if col in (0, 2, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.product_table.setItem(row, col, item)

            add_row_button = QPushButton("+")
            add_row_button.setToolTip("Add one unit to the current bill")
            add_row_button.clicked.connect(
                lambda checked=False, product_id=product["id"]:
                    self.add_product_to_cart(product_id)
            )
            self.product_table.setCellWidget(row, 4, add_row_button)

            remove_row_button = QPushButton("−")
            remove_row_button.setToolTip(
                "Reduce quantity in the current bill; removes it at zero"
            )
            remove_row_button.clicked.connect(
                lambda checked=False, product_id=product["id"]:
                    self.remove_product_from_cart(product_id)
            )
            self.product_table.setCellWidget(row, 5, remove_row_button)

        self.product_table.setColumnWidth(4, 48)
        self.product_table.setColumnWidth(5, 48)

    def add_product_to_cart(self, product_id):
        """Add one unit of a product to the current bill."""
        row = None
        for index in range(self.product_table.rowCount()):
            id_item = self.product_table.item(index, 0)
            if id_item and int(id_item.text()) == int(product_id):
                row = index
                break

        if row is None:
            return

        product_name = self.product_table.item(row, 1).text()
        price = float(
            self.product_table.item(row, 2).text().replace("₹", "").strip()
        )
        available_stock = int(self.product_table.item(row, 3).text())

        existing = next(
            (item for item in self.cart
             if item["product_id"] == int(product_id)),
            None
        )
        current_quantity = existing["quantity"] if existing else 0

        if current_quantity >= available_stock:
            QMessageBox.warning(
                self, "Stock Limit",
                "Requested quantity exceeds available stock."
            )
            return

        if existing:
            existing["quantity"] += 1
        else:
            self.cart.append({
                "product_id": int(product_id),
                "product_name": product_name,
                "quantity": 1,
                "price": price,
                "available_stock": available_stock
            })

        self.refresh_cart()

    def remove_product_from_cart(self, product_id):
        """Reduce one unit of a product in the current bill."""
        existing = next(
            (item for item in self.cart
             if item["product_id"] == int(product_id)),
            None
        )

        if not existing:
            QMessageBox.information(
                self, "Product Not in Bill",
                "This product has not been added to the current bill."
            )
            return

        existing["quantity"] -= 1
        if existing["quantity"] <= 0:
            self.cart.remove(existing)

        self.refresh_cart()

    def add_selected_product(self):

        row = self.product_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Select Product",
                "Please select a product."
            )
            return

        product_id = int(
            self.product_table.item(row, 0).text()
        )

        product_name = self.product_table.item(row, 1).text()

        price = float(
            self.product_table.item(row, 2).text()
            .replace("₹", "")
            .strip()
        )

        available_stock = int(
            self.product_table.item(row, 3).text()
        )

        existing = next(
            (
                item for item in self.cart
                if item["product_id"] == product_id
            ),
            None
        )

        current_quantity = (
            existing["quantity"] if existing else 0
        )

        if current_quantity >= available_stock:

            QMessageBox.warning(
                self,
                "Stock Limit",
                "Requested quantity exceeds available stock."
            )
            return

        if existing:
            existing["quantity"] += 1

        else:

            self.cart.append({
                "product_id": product_id,
                "product_name": product_name,
                "quantity": 1,
                "price": price,
                "available_stock": available_stock
            })

        self.refresh_cart()
    def add_new_product(self):
        dialog = ProductDialog(self)

        if dialog.exec():
            # Clear any existing search and refresh the available-products list.
            self.search_input.clear()
            self.load_products()

    def change_quantity(self, change):

        row = self.cart_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Select Item",
                "Please select a cart item."
            )
            return

        item = self.cart[row]

        new_quantity = item["quantity"] + change

        if new_quantity <= 0:
            item["quantity"] = 1
            QMessageBox.information(
                self,
                "Quantity",
                "Use Remove Item to remove a product."
            )
            return

        if new_quantity > item["available_stock"]:

            QMessageBox.warning(
                self,
                "Stock Limit",
                "Requested quantity exceeds available stock."
            )
            return

        item["quantity"] = new_quantity

        self.refresh_cart()

    def remove_selected_item(self):

        row = self.cart_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Select Item",
                "Please select a cart item."
            )
            return

        self.cart.pop(row)

        self.refresh_cart()

    def refresh_cart(self):

        self.cart_table.setRowCount(0)

        for item in self.cart:

            row = self.cart_table.rowCount()

            self.cart_table.insertRow(row)

            amount = item["quantity"] * item["price"]

            values = [
                item["product_id"],
                item["product_name"],
                item["quantity"],
                f"₹ {item['price']:.2f}",
                f"₹ {amount:.2f}"
            ]

            for col, value in enumerate(values):

                self.cart_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(value))
                )

        self.update_totals()

    def update_totals(self):

        subtotal = sum(
            item["quantity"] * item["price"]
            for item in self.cart
        )

        discount = self.discount_input.value()

        if discount > subtotal:
            discount = subtotal

        from database.db import get_setting

        tax_enabled = get_setting("tax_enabled", "0") == "1"

        tax_rate = (
            float(get_setting("default_tax_rate", "0"))
            if tax_enabled else 0
        )

        taxable_amount = max(0, subtotal - discount)

        tax = round(
            taxable_amount * tax_rate / 100,
            2
        )

        total = round(taxable_amount + tax, 2)

        self.tax_label.setText(
            f"Tax: ₹ {tax:.2f}"
        )

        self.total_label.setText(
            f"Total: ₹ {total:.2f}"
        )

    def clear_bill(self):

        self.cart.clear()

        self.customer_name.clear()
        self.customer_phone.clear()
        self.customer_address.clear()

        self.discount_input.setValue(0)

        self.last_invoice = None

        self.refresh_cart()

    def complete_sale(self):

        if not self.cart:

            QMessageBox.warning(
                self,
                "Empty Bill",
                "Add products before completing the sale."
            )
            return

        try:

            result = save_sale(
                customer_name=self.customer_name.text(),
                customer_phone=self.customer_phone.text(),
                customer_address=self.customer_address.text(),
                cart=self.cart,
                discount=self.discount_input.value(),
                payment_method=self.payment_method.currentText()
            )

            self.last_invoice = result

            self.cart.clear()

            self.discount_input.setValue(0)

            self.load_products()
            self.refresh_cart()

            QMessageBox.information(
                self,
                "Sale Completed",
                (
                    f"Invoice: {result['invoice_number']}\n"
                    f"Total: ₹ {result['grand_total']:.2f}\n\n"
                    "Sale saved successfully."
                )
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Billing Error",
                str(exc)
            )

    def open_invoice(self):

        if not self.last_invoice:

            QMessageBox.warning(
                self,
                "No Invoice",
                "Complete a sale before generating its invoice."
            )
            return

        try:

            path = generate_invoice(self.last_invoice)

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(Path(path).resolve()))
            )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Invoice Error",
                str(exc)
            )