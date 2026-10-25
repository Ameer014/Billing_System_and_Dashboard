from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from database.db import get_connection, get_setting


def money(value):
    """Round a value to two decimal places."""

    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def get_products(search=""):

    with get_connection() as conn:

        return conn.execute(
            """
            SELECT
                id,
                product_code,
                product_name,
                selling_price,
                purchase_price,
                stock_quantity
            FROM products
            WHERE is_active = 1
              AND product_name LIKE ?
            ORDER BY product_name
            """,
            (f"%{search}%",)
        ).fetchall()


def save_sale(
    customer_name,
    customer_phone,
    customer_address,
    cart,
    discount,
    payment_method
):
    """
    Save a sale and update stock atomically.

    cart example:
    [
        {"product_id": 1, "quantity": 2},
        {"product_id": 3, "quantity": 1}
    ]
    """

    if not cart:
        raise ValueError("Add at least one product.")

    customer_name = customer_name.strip() or "Walk-in Customer"

    discount = money(discount)

    if discount < 0:
        raise ValueError("Discount cannot be negative.")

    with get_connection() as conn:

        # This context manager commits on success and rolls back
        # if an exception occurs.
        conn.execute("BEGIN IMMEDIATE")

        # Create customer record only when contact details exist.
        customer_id = None

        if customer_name != "Walk-in Customer" or customer_phone.strip():

            existing_customer = None

            if customer_phone.strip():

                existing_customer = conn.execute(
                    """
                    SELECT id
                    FROM customers
                    WHERE phone = ?
                    ORDER BY id
                    LIMIT 1
                    """,
                    (customer_phone.strip(),)
                ).fetchone()

            if existing_customer:
                customer_id = existing_customer["id"]

                conn.execute(
                    """
                    UPDATE customers
                    SET customer_name = ?,
                        address = ?
                    WHERE id = ?
                    """,
                    (
                        customer_name,
                        customer_address.strip(),
                        customer_id
                    )
                )

            else:

                cursor = conn.execute(
                    """
                    INSERT INTO customers
                    (customer_name, phone, address)
                    VALUES (?, ?, ?)
                    """,
                    (
                        customer_name,
                        customer_phone.strip(),
                        customer_address.strip()
                    )
                )

                customer_id = cursor.lastrowid

        # Fetch products from the database rather than trusting
        # prices supplied by the interface.
        normalized_cart = {}

        for item in cart:

            product_id = int(item["product_id"])
            quantity = int(item["quantity"])

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            normalized_cart[product_id] = (
                normalized_cart.get(product_id, 0) + quantity
            )

        sale_lines = []
        subtotal = Decimal("0.00")

        for product_id, quantity in normalized_cart.items():

            product = conn.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                  AND is_active = 1
                """,
                (product_id,)
            ).fetchone()

            if product is None:
                raise ValueError("A selected product no longer exists.")

            if product["stock_quantity"] < quantity:
                raise ValueError(
                    f"Insufficient stock for {product['product_name']}."
                )

            unit_price = money(product["selling_price"])
            unit_cost = money(product["purchase_price"])

            line_total = money(unit_price * quantity)

            subtotal += line_total

            sale_lines.append({
                "product_id": product_id,
                "product_name": product["product_name"],
                "quantity": quantity,
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "line_total": line_total
            })

        subtotal = money(subtotal)

        if discount > subtotal:
            raise ValueError("Discount cannot exceed subtotal.")

        tax_enabled = get_setting("tax_enabled", "0") == "1"

        tax_rate = Decimal(
            get_setting("default_tax_rate", "0")
        ) if tax_enabled else Decimal("0")

        taxable_amount = money(subtotal - discount)

        tax_amount = money(
            taxable_amount * tax_rate / Decimal("100")
        )

        grand_total = money(taxable_amount + tax_amount)

        invoice_prefix = get_setting("invoice_prefix", "INV")

        # Create the invoice number under the same write transaction.
        next_id = conn.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM invoices"
        ).fetchone()[0]

        invoice_number = f"{invoice_prefix}-{next_id:06d}"

        invoice_date = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        cursor = conn.execute(
            """
            INSERT INTO invoices (
                invoice_number,
                customer_id,
                invoice_date,
                subtotal,
                discount,
                tax_amount,
                grand_total,
                payment_method,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
            """,
            (
                invoice_number,
                customer_id,
                invoice_date,
                float(subtotal),
                float(discount),
                float(tax_amount),
                float(grand_total),
                payment_method
            )
        )

        invoice_id = cursor.lastrowid

        for line in sale_lines:

            # Reduce stock and reject unexpected stock changes.
            result = conn.execute(
                """
                UPDATE products
                SET stock_quantity = stock_quantity - ?
                WHERE id = ?
                  AND stock_quantity >= ?
                """,
                (
                    line["quantity"],
                    line["product_id"],
                    line["quantity"]
                )
            )

            if result.rowcount != 1:
                raise ValueError("Stock changed. Please try again.")

            conn.execute(
                """
                INSERT INTO invoice_items (
                    invoice_id,
                    product_id,
                    product_name,
                    quantity,
                    unit_price,
                    unit_cost,
                    discount,
                    tax_rate,
                    tax_amount,
                    line_total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_id,
                    line["product_id"],
                    line["product_name"],
                    line["quantity"],
                    float(line["unit_price"]),
                    float(line["unit_cost"]),
                    0,
                    float(tax_rate),
                    0,
                    float(line["line_total"])
                )
            )

            conn.execute(
                """
                INSERT INTO stock_movements (
                    product_id,
                    movement_type,
                    quantity,
                    reference
                )
                VALUES (?, 'SALE', ?, ?)
                """,
                (
                    line["product_id"],
                    -line["quantity"],
                    invoice_number
                )
            )

        conn.execute(
            """
            INSERT INTO payments (
                invoice_id,
                payment_method,
                amount,
                payment_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                invoice_id,
                payment_method,
                float(grand_total),
                invoice_date
            )
        )

    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "subtotal": float(subtotal),
        "discount": float(discount),
        "tax_amount": float(tax_amount),
        "grand_total": float(grand_total),
        "payment_method": payment_method,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_address": customer_address,
        "items": sale_lines
    }