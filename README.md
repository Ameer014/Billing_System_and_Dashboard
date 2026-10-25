# Billing System and Dashboard

### Offline Desktop Billing and Sales Management System

Billing System and Dashboard is a Python-based desktop application designed to simplify product management, billing, inventory tracking, and sales monitoring for small retail businesses.

## Features

* Product management and product search
* Add and remove products from the current bill
* Quantity management and stock validation
* Customer information management during billing
* Automatic subtotal, discount, tax, and total calculations
* Invoice generation in PDF format
* SQLite database for local data storage
* Dashboard for sales monitoring
* Shop settings and invoice customization

## Technology Stack

* **Language:** Python
* **Desktop UI:** PySide6
* **Database:** SQLite
* **PDF Generation:** ReportLab
* **Data Analysis:** Pandas
* **Visualization:** Matplotlib

## Project Structure

```text
SmartShopPOS/
├── main.py
├── requirements.txt
├── database/
├── ui/
├── services/
├── assets/
├── reports/
└── backups/
```

## Getting Started

### Prerequisites

* Python 3.11 or another compatible Python version
* Git

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/SmartShopPOS.git
cd SmartShopPOS
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

The application initializes its local database according to the database initialization code.

## Data and Privacy

The application is designed for local database storage. The repository does not include real customer records, local database files, or generated invoices.

## Future Improvements

* Barcode scanning
* Advanced sales analytics
* Automatic database backups
* Export sales reports to Excel
* Multi-computer access
* Standalone Windows executable

## Author

Developed as a desktop software project using Python and SQLite.
