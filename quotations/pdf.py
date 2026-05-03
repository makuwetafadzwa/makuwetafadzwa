"""PDF generation for quotations using ReportLab."""
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _money(value, currency="$"):
    return f"{currency}{Decimal(value or 0):,.2f}"


def build_quotation_pdf(buffer, quotation):
    from company_settings.models import CompanyProfile

    company = CompanyProfile.objects.first()
    currency = (company.currency_symbol if company else "$")
    company_name = company.name if company else "Aluflow"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Quotation {quotation.quote_number}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=4,
    )
    h2_style = ParagraphStyle("h2", parent=styles["Heading3"], textColor=colors.HexColor("#0f172a"))
    body_style = styles["BodyText"]
    small = ParagraphStyle("small", parent=body_style, fontSize=9, textColor=colors.HexColor("#475569"))

    story = []
    # Header — logo (if any) + company name on the left, quote # on the right
    logo_flowable = ""
    if company and company.logo:
        try:
            logo_flowable = Image(company.logo.path, width=30 * mm, height=30 * mm, kind="proportional")
        except Exception:
            logo_flowable = ""
    company_block = [Paragraph(f"<b>{company_name}</b>", title_style)]
    if company and company.tagline:
        company_block.append(Paragraph(company.tagline, small))
    left_cell = [logo_flowable, *company_block] if logo_flowable else company_block
    header_data = [
        [
            left_cell,
            Paragraph(f"<b>QUOTATION</b><br/>{quotation.quote_number} v{quotation.version}", h2_style),
        ]
    ]
    if company:
        header_data.append([
            Paragraph(
                f"{company.address or ''}<br/>{company.phone or ''} · {company.email or ''}",
                small,
            ),
            Paragraph(
                f"Issue date: {quotation.issue_date}<br/>"
                + (f"Valid until: {quotation.valid_until}<br/>" if quotation.valid_until else "")
                + f"Status: {quotation.get_status_display()}",
                small,
            ),
        ])
    header = Table(header_data, colWidths=[100 * mm, 70 * mm])
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header)
    story.append(Spacer(1, 8 * mm))

    # Customer block
    cust = quotation.customer
    bill_to = (
        f"<b>Bill To:</b><br/>{cust.display_name}<br/>"
        f"{cust.address_line1 or ''}<br/>{cust.city or ''}<br/>"
        f"{cust.phone or ''} · {cust.email or ''}"
    )
    project = (
        f"<b>Project:</b><br/>{quotation.project.name}<br/>{quotation.project.site_address or ''}"
        if quotation.project
        else ""
    )
    block = Table([[Paragraph(bill_to, body_style), Paragraph(project, body_style)]], colWidths=[85 * mm, 85 * mm])
    block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(block)
    story.append(Spacer(1, 6 * mm))

    # Items table
    rows = [["#", "Description", "Size (mm)", "Qty", "Unit Price", "Total"]]
    for idx, item in enumerate(quotation.items.all(), start=1):
        size = (
            f"{item.width_mm}×{item.height_mm}"
            if item.width_mm and item.height_mm
            else "—"
        )
        rows.append([
            idx,
            Paragraph(item.description, body_style),
            size,
            f"{item.quantity:g}",
            _money(item.unit_price, currency),
            _money(item.line_total, currency),
        ])
    items_table = Table(
        rows,
        colWidths=[10 * mm, 70 * mm, 25 * mm, 15 * mm, 25 * mm, 25 * mm],
        repeatRows=1,
    )
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # Totals
    totals_rows = [
        ["Subtotal", _money(quotation.subtotal, currency)],
        [f"Discount ({quotation.discount_percent:g}%)", "-" + _money(quotation.discount_amount, currency)],
        [f"VAT ({quotation.tax_percent:g}%)", _money(quotation.tax_amount, currency)],
        ["Total", _money(quotation.grand_total, currency)],
    ]
    totals = Table(totals_rows, colWidths=[40 * mm, 30 * mm], hAlign="RIGHT")
    totals.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1e3a8a")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(totals)
    story.append(Spacer(1, 8 * mm))

    if quotation.notes:
        story.append(Paragraph("<b>Notes</b>", h2_style))
        story.append(Paragraph(quotation.notes.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 4 * mm))
    if quotation.terms:
        story.append(Paragraph("<b>Terms & Conditions</b>", h2_style))
        story.append(Paragraph(quotation.terms.replace("\n", "<br/>"), small))

    doc.build(story)
