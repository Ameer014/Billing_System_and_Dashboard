from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

invoice_path = OUTPUT_DIR / "sample_invoice.pdf"

# Replace these with your actual shop details.
shop = {
    "name": "YOUR SHOP NAME",
    "tagline": "CCTV & Computer Sales and Service",
    "address": "Your Shop Address",
    "phone": "Your Phone Number",
    "email": "your@email.com",
}

customer = {
    "name": "Sample Customer",
    "phone": "9876543210",
}

invoice = {
    "number": "INV-0001",
    "date": "20-10-2026",
    "payment_method": "UPI",
}

items = [
    {
        "name": "CCTV Camera",
        "quantity": 2,
        "price": 2500.00,
    },
    {
        "name": "Hard Disk 1TB",
        "quantity": 1,
        "price": 4000.00,
    },
]

discount = 200.00
tax_rate = 0.00  # Demo only; configure the actual applicable rate.

subtotal = sum(
    item["quantity"] * item["price"]
    for item in items
)

taxable_amount = max(0, subtotal - discount)
tax_amount = taxable_amount * tax_rate / 100
grand_total = taxable_amount + tax_amount

doc = SimpleDocTemplate(
    str(invoice_path),
    pagesize=A4,
    rightMargin=18 * mm,
    leftMargin=18 * mm,
    topMargin=15 * mm,
    bottomMargin=15 * mm,
)

styles = getSampleStyleSheet()
story = []

# Logo, if available.
logo_path = Path("assets/logo.png")

if logo_path.exists():
    logo = Image(
        str(logo_path),
        width=25 * mm,
        height=25 * mm,
    )
else:
    logo = Paragraph(
        "<b>SHOP LOGO</b>",
        styles["Normal"],
    )

shop_details = Paragraph(
    f"""
    <font size="17"><b>{shop['name']}</b></font><br/>
    {shop['tagline']}<br/>
    {shop['address']}<br/>
    Phone: {shop['phone']}<br/>
    Email: {shop['email']}
    """,
    styles["Normal"],
)

header = Table(
    [[logo, shop_details]],
    colWidths=[32 * mm, 145 * mm],
)

header.setStyle(
    TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ])
)

story.append(header)
story.append(Spacer(1, 5 * mm))

story.append(
    Paragraph(
        "<b><font size='15'>INVOICE</font></b>",
        styles["Title"],
    )
)

story.append(Spacer(1, 5 * mm))

customer_data = [
    ["Invoice Number", invoice["number"],
     "Date", invoice["date"]],

    ["Customer Name", customer["name"],
     "Mobile", customer["phone"]],
]

customer_table = Table(
    customer_data,
    colWidths=[32 * mm, 55 * mm, 25 * mm, 65 * mm],
)

customer_table.setStyle(
    TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ])
)

story.append(customer_table)
story.append(Spacer(1, 8 * mm))

table_data = [
    ["No.", "Product", "Qty", "Unit Price", "Amount"]
]

for index, item in enumerate(items, start=1):
    amount = item["quantity"] * item["price"]

    table_data.append([
        str(index),
        item["name"],
        str(item["quantity"]),
        f"Rs. {item['price']:,.2f}",
        f"Rs. {amount:,.2f}",
    ])

product_table = Table(
    table_data,
    colWidths=[12 * mm, 72 * mm, 16 * mm, 35 * mm, 42 * mm],
    repeatRows=1,
)

product_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ])
)

story.append(product_table)
story.append(Spacer(1, 8 * mm))

totals = [
    ["Subtotal", f"Rs. {subtotal:,.2f}"],
    ["Discount", f"Rs. {discount:,.2f}"],
    [f"Tax ({tax_rate:.2f}%)", f"Rs. {tax_amount:,.2f}"],
    ["GRAND TOTAL", f"Rs. {grand_total:,.2f}"],
]

totals_table = Table(
    totals,
    colWidths=[55 * mm, 45 * mm],
    hAlign="RIGHT",
)

totals_table.setStyle(
    TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(totals_table)
story.append(Spacer(1, 8 * mm))

story.append(
    Paragraph(
        f"Payment Method: {invoice['payment_method']}",
        styles["Normal"],
    )
)

story.append(Spacer(1, 15 * mm))

signature_table = Table(
    [[
        "Customer Signature",
        "Authorized Signature",
    ]],
    colWidths=[85 * mm, 85 * mm],
)

signature_table.setStyle(
    TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ])
)

story.append(signature_table)

doc.build(story)

print(f"Invoice created: {invoice_path}")