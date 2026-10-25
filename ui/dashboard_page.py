from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from PySide6.QtCore import Qt

from database.db import get_connection


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)

        title = QLabel("Dashboard & Sales")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        root.addWidget(title)

        # ---------------- KPI CARDS ----------------

        cards_layout = QHBoxLayout()

        self.today_sales = self.create_card(
            cards_layout,
            "Today's Sales"
        )

        self.month_sales = self.create_card(
            cards_layout,
            "Monthly Sales"
        )

        self.total_invoices = self.create_card(
            cards_layout,
            "Total Invoices"
        )

        self.gross_profit = self.create_card(
            cards_layout,
            "Gross Profit"
        )

        root.addLayout(cards_layout)

        # ---------------- SALES TABLE ----------------

        root.addWidget(
            QLabel("Recent Sales")
        )

        self.sales_table = QTableWidget(0, 5)

        self.sales_table.setHorizontalHeaderLabels([
            "Invoice",
            "Date",
            "Customer",
            "Payment",
            "Total",
        ])

        self.sales_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.sales_table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        self.sales_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        root.addWidget(self.sales_table)

        self.refresh_data()

    def create_card(self, layout, title):

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E1E6EF;
                border-radius: 8px;
            }
        """)

        card_layout = QVBoxLayout(frame)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 12px; color: #667085;"
        )

        value_label = QLabel("₹ 0.00")
        value_label.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        layout.addWidget(frame)

        return value_label

    def refresh_data(self):

        with get_connection() as conn:

            today = conn.execute(
                """
                SELECT COALESCE(SUM(grand_total), 0)
                FROM invoices
                WHERE status = 'COMPLETED'
                  AND date(invoice_date, 'localtime') =
                      date('now', 'localtime')
                """
            ).fetchone()[0]

            monthly = conn.execute(
                """
                SELECT COALESCE(SUM(grand_total), 0)
                FROM invoices
                WHERE status = 'COMPLETED'
                  AND strftime('%Y-%m', invoice_date, 'localtime') =
                      strftime('%Y-%m', 'now', 'localtime')
                """
            ).fetchone()[0]

            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM invoices
                WHERE status = 'COMPLETED'
                """
            ).fetchone()[0]

            profit = conn.execute(
                """
                SELECT COALESCE(
                    SUM(
                        ii.line_total -
                        (ii.quantity * ii.unit_cost)
                    ),
                    0
                )
                FROM invoice_items ii
                JOIN invoices i
                    ON i.id = ii.invoice_id
                WHERE i.status = 'COMPLETED'
                """
            ).fetchone()[0]

            recent_sales = conn.execute(
                """
                SELECT
                    i.invoice_number,
                    i.invoice_date,
                    COALESCE(c.customer_name, 'Walk-in Customer')
                        AS customer_name,
                    i.payment_method,
                    i.grand_total
                FROM invoices i
                LEFT JOIN customers c
                    ON c.id = i.customer_id
                WHERE i.status = 'COMPLETED'
                ORDER BY i.id DESC
                LIMIT 100
                """
            ).fetchall()

        self.today_sales.setText(
            f"₹ {today:,.2f}"
        )

        self.month_sales.setText(
            f"₹ {monthly:,.2f}"
        )

        self.total_invoices.setText(
            str(count)
        )

        self.gross_profit.setText(
            f"₹ {profit:,.2f}"
        )

        self.sales_table.setRowCount(0)

        for sale in recent_sales:

            row = self.sales_table.rowCount()

            self.sales_table.insertRow(row)

            values = [
                sale["invoice_number"],
                sale["invoice_date"],
                sale["customer_name"],
                sale["payment_method"],
                f"₹ {sale['grand_total']:,.2f}",
            ]

            for col, value in enumerate(values):

                self.sales_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(value))
                )