from pathlib import Path
from xml.sax.saxutils import escape

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

from database.db import get_setting


APP_DIR = Path.home() / "SmartShopPOS"

REPORT_DIR = APP_DIR / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def safe_text(value):
    return escape(str(value or ""))


def generate_invoice(invoice):

    invoice_number = invoice["invoice_number"]

    output_path = REPORT_DIR / f"{invoice_number}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    # ---------------- SHOP DETAILS ----------------

    shop_name = get_setting(
        "shop_name",
        "YOUR SHOP NAME"
    )

    tagline = get_setting(
        "tagline",
        "CCTV & Computer Sales and Service"
    )

    address = get_setting("address", "")
    phone = get_setting("phone", "")
    email = get_setting("email", "")
    logo_path = get_setting("logo_path", "")

    shop_html = (
        f"<font size='18'><b>{safe_text(shop_name)}</b></font><br/>"
        f"{safe_text(tagline)}<br/>"
        f"{safe_text(address)}<br/>"
        f"Phone: {safe_text(phone)}<br/>"
        f"Email: {safe_text(email)}"
    )

    shop_paragraph = Paragraph(
        shop_html,
        styles["Normal"]
    )

    logo_cell = Paragraph(
        "<b>LOGO</b>",
        styles["Normal"]
    )

    if logo_path and Path(logo_path).is_file():

        logo_cell = Image(
            logo_path,
            width=25 * mm,
            height=25 * mm,
            kind="proportional"
        )

    header = Table(
        [[logo_cell, shop_paragraph]],
        colWidths=[35 * mm, 145 * mm]
    )

    header.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, -1), 1, colors.grey),
        ])
    )

    story.append(header)

    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "<b><font size='16'>INVOICE</font></b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 5 * mm))

    # ---------------- CUSTOMER DETAILS ----------------

    customer_name = invoice.get(
        "customer_name",
        "Walk-in Customer"
    )

    customer_phone = invoice.get(
        "customer_phone",
        ""
    )

    customer_address = invoice.get(
        "customer_address",
        ""
    )

    invoice_date = invoice.get(
        "invoice_date",
        ""
    )

    customer_data = [
        [
            "Invoice Number",
            safe_text(invoice_number),
            "Date",
            safe_text(invoice_date),
        ],
        [
            "Customer",
            safe_text(customer_name),
            "Phone",
            safe_text(customer_phone),
        ],
        [
            "Address",
            safe_text(customer_address),
            "",
            "",
        ],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[30 * mm, 65 * mm, 22 * mm, 63 * mm],
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

    story.append(Spacer(1, 7 * mm))

    # ---------------- PRODUCT TABLE ----------------

    table_data = [[
        "No.",
        "Product",
        "Qty",
        "Unit Price",
        "Amount",
    ]]

    for index, item in enumerate(
        invoice.get("items", []),
        start=1
    ):

        table_data.append([
            str(index),
            safe_text(item["product_name"]),
            str(item["quantity"]),
            f"Rs. {float(item['unit_price']):,.2f}",
            f"Rs. {float(item['line_total']):,.2f}",
        ])

    product_table = Table(
        table_data,
        colWidths=[
            12 * mm,
            76 * mm,
            16 * mm,
            35 * mm,
            41 * mm,
        ],
        repeatRows=1,
    )

    product_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F3A5F")
            ),
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

    story.append(Spacer(1, 7 * mm))

    # ---------------- TOTALS ----------------

    totals_data = [
        ["Subtotal", f"Rs. {invoice['subtotal']:,.2f}"],
        ["Discount", f"Rs. {invoice['discount']:,.2f}"],
        ["Tax", f"Rs. {invoice['tax_amount']:,.2f}"],
        ["GRAND TOTAL", f"Rs. {invoice['grand_total']:,.2f}"],
    ]

    totals_table = Table(
        totals_data,
        colWidths=[45 * mm, 45 * mm],
        hAlign="RIGHT"
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

    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "Payment Method: "
            + safe_text(invoice.get("payment_method", "")),
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15 * mm))

    # ---------------- SIGNATURES ----------------

    signatures = Table(
        [[
            "Customer Signature",
            "Authorized Signature",
        ]],
        colWidths=[85 * mm, 85 * mm],
    )

    signatures.setStyle(
        TableStyle([
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(signatures)

    story.append(Spacer(1, 8 * mm))

    footer = get_setting(
        "invoice_footer",
        "Thank you for your business!"
    )

    story.append(
        Paragraph(
            f"<para align='center'>{safe_text(footer)}</para>",
            styles["Normal"]
        )
    )

    doc.build(story)

    return str(output_path)