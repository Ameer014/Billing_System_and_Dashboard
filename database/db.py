import sqlite3
from pathlib import Path


# Store application data separately from the source files.
APP_DIR = Path.home() / "SmartShopPOS"

DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "smartshop.db"


def get_connection():
    """Create a connection to the local SQLite database."""

    conn = sqlite3.connect(DB_PATH, timeout=10)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def initialize_database():
    """Create all required database tables."""

    with get_connection() as conn:

        conn.executescript("""

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE,
            product_name TEXT NOT NULL,
            category TEXT,
            brand TEXT,
            purchase_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 5,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );


        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );


        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL UNIQUE,
            customer_id INTEGER,
            invoice_date TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            grand_total REAL NOT NULL,
            payment_method TEXT,
            status TEXT NOT NULL DEFAULT 'COMPLETED',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (customer_id)
                REFERENCES customers(id)
        );


        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            unit_cost REAL NOT NULL DEFAULT 0,
            discount REAL NOT NULL DEFAULT 0,
            tax_rate REAL NOT NULL DEFAULT 0,
            tax_amount REAL NOT NULL DEFAULT 0,
            line_total REAL NOT NULL,

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id),

            FOREIGN KEY (product_id)
                REFERENCES products(id)
        );


        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id)
        );


        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reference TEXT,
            movement_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
                REFERENCES products(id)
        );


        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        );


        CREATE TABLE IF NOT EXISTS shop_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        );


        """)

        # Default settings.
        defaults = {
            "shop_name": "YOUR SHOP NAME",
            "tagline": "CCTV & Computer Sales and Service",
            "address": "",
            "phone": "",
            "email": "",
            "logo_path": "",
            "tax_enabled": "0",
            "default_tax_rate": "0",
            "invoice_prefix": "INV",
            "invoice_footer": "Thank you for your business!"
        }

        conn.executemany(
            """
            INSERT OR IGNORE INTO shop_settings
            (setting_key, setting_value)
            VALUES (?, ?)
            """,
            defaults.items()
        )

    print(f"Database initialized: {DB_PATH}")


def get_setting(key, default=""):
    """Read one setting from the database."""

    with get_connection() as conn:

        row = conn.execute(
            """
            SELECT setting_value
            FROM shop_settings
            WHERE setting_key = ?
            """,
            (key,)
        ).fetchone()

    if row is None:
        return default

    return row["setting_value"]


def save_setting(key, value):
    """Save or update one setting."""

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO shop_settings
            (setting_key, setting_value)
            VALUES (?, ?)

            ON CONFLICT(setting_key)
            DO UPDATE SET setting_value = excluded.setting_value
            """,
            (key, str(value))
        )


if __name__ == "__main__":
    initialize_database()