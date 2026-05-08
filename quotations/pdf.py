"""PDF generation for quotations using ReportLab.

Produces a professional A4 quotation in the style commonly used by
Aluflow Investments — logo + address top-left, big QUOTATION + meta
table top-right, customer info bar, itemised table with subtotal /
deposit / balance, terms, customer-acceptance signature box, and
banking details at the foot.

Multi-page quotes are handled automatically — the items table splits
across pages with the column header repeating, and pages 2+ get a
"<quote_no> (continued)" header line.
"""
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from core.pdf_base import (
    build_aluflow_document,
    get_styles,
    money,
    render_aluflow_pdf,
)


DEPOSIT_PERCENT = Decimal("75")  # company-wide default deposit on acceptance


def build_quotation_pdf(buffer, quotation):
    from company_settings.models import CompanyProfile

    company = CompanyProfile.objects.first()
    sym = company.currency_symbol if company else "$"
    company_name = company.name if company else "Aluflow"

    doc = build_aluflow_document(
        buffer,
        title=f"Quotation {quotation.quote_number}",
        author=company_name,
    )

    s = get_styles()
    body, body_sm = s["body"], s["body_sm"]
    huge_title = s["huge_title"]
    label, value = s["label"], s["value"]
    section_header = s["section_header"]
    italic_tagline = s["tagline"]

    story = []

    # ------- 1. HEADER ROW -------
    left_cell = []
    if company and company.logo:
        try:
            left_cell.append(
                Image(company.logo.path, width=35 * mm, height=35 * mm, kind="proportional")
            )
            left_cell.append(Spacer(1, 3 * mm))
        except Exception:
            pass

    addr_lines = []
    if company:
        if company.address:
            city_part = f", {company.city}" if company.city else ""
            addr_lines.append(f"{company.address}{city_part}")
        elif company.city:
            addr_lines.append(company.city)
        if company.phone:
            addr_lines.append(f"Phone: {company.phone}")
        if company.email:
            addr_lines.append(company.email)
    if addr_lines:
        left_cell.append(Paragraph("<br/>".join(addr_lines), body_sm))

    quotation_word = Paragraph("QUOTATION", huge_title)
    valid_until = (
        quotation.valid_until.strftime("%d/%m/%Y") if quotation.valid_until else "—"
    )
    meta_table = Table(
        [
            [Paragraph("QUOTE #", label), Paragraph("DATE", label)],
            [
                Paragraph(quotation.quote_number, value),
                Paragraph(quotation.issue_date.strftime("%d/%m/%Y"), value),
            ],
            [Paragraph("REF", label), Paragraph("VALID UNTIL", label)],
            [
                Paragraph(quotation.recipient_code, value),
                Paragraph(valid_until, value),
            ],
        ],
        colWidths=[40 * mm, 35 * mm],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d1d5db")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#d1d5db")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#374151")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#374151")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    header = Table(
        [[left_cell, [quotation_word, Spacer(1, 4 * mm), meta_table]]],
        colWidths=[100 * mm, 80 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 5 * mm))

    # ------- 2. RECIPIENT INFO + PREPARED BY -------
    customer_header = Table(
        [[Paragraph("CUSTOMER INFO", section_header)]],
        colWidths=[80 * mm],
    )
    customer_header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#9ca3af")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#374151")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    cust_lines = [quotation.recipient_name]
    cust = quotation.customer
    if cust:
        if (
            cust.company_name
            and getattr(cust, "customer_type", "") != "individual"
            and cust.company_name != cust.full_name
        ):
            cust_lines.append(cust.company_name)
        if cust.address_line1:
            cust_lines.append(cust.address_line1)
        if cust.city:
            cust_lines.append(f"{cust.city}, {cust.country}")
    elif quotation.lead:
        if quotation.lead.company:
            cust_lines.append(quotation.lead.company)
        if quotation.lead.address:
            cust_lines.append(quotation.lead.address)
        if quotation.lead.city:
            cust_lines.append(quotation.lead.city)

    contact_bits = " · ".join(
        filter(None, [quotation.recipient_phone, quotation.recipient_email])
    )
    if contact_bits:
        cust_lines.append(contact_bits)
    customer_text = Paragraph("<br/>".join(cust_lines), body_sm)

    prepared_by_user = ""
    if quotation.created_by:
        prepared_by_user = (
            quotation.created_by.get_full_name() or quotation.created_by.username
        )
    prepared_by = Paragraph(
        f"<i>Prepared By:</i><br/><b>{prepared_by_user}</b>", body_sm
    )

    cust_row = Table(
        [
            [
                [customer_header, Spacer(1, 3 * mm), customer_text],
                [Spacer(1, 12 * mm), prepared_by],
            ]
        ],
        colWidths=[100 * mm, 80 * mm],
    )
    cust_row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(cust_row)
    story.append(Spacer(1, 4 * mm))

    # ------- 3. ITEMS TABLE (splits across pages, header repeats) -------
    items = list(quotation.items.all())
    rows = [["DESCRIPTION", "SIZE", "QTY", "UNIT PRICE", "AMOUNT"]]
    for item in items:
        size = (
            f"{item.width_mm} x {item.height_mm}"
            if item.width_mm and item.height_mm
            else ""
        )
        rows.append(
            [
                Paragraph(item.description, body_sm),
                size,
                f"{item.quantity:g}",
                money(item.unit_price),
                money(item.line_total),
            ]
        )
    # Pad with a few blank rows for visual balance only when the quote is short
    if len(items) <= 5:
        for _ in range(max(0, 5 - len(items))):
            rows.append(["", "", "", "", ""])

    items_table = Table(
        rows,
        colWidths=[70 * mm, 35 * mm, 15 * mm, 30 * mm, 30 * mm],
        repeatRows=1,  # repeat the column header on every continuation page
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d1d5db")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black),
                ("LINEAFTER", (0, 0), (-2, -1), 0.4, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(items_table)

    # ------- 4. TAGLINE + TOTALS -------
    deposit_pct = DEPOSIT_PERCENT
    deposit_amt = (quotation.grand_total * deposit_pct / Decimal("100")).quantize(Decimal("0.01"))
    balance = (quotation.grand_total - deposit_amt).quantize(Decimal("0.01"))

    totals_data = [["SUBTOTAL", money(quotation.subtotal)]]
    if quotation.discount_amount > 0:
        totals_data.append(
            [f"DISCOUNT ({quotation.discount_percent:g}%)", "-" + money(quotation.discount_amount)]
        )
        totals_data.append(["TOTAL", money(quotation.grand_total)])
    totals_data.append([f"DEPOSIT ({deposit_pct:g}%)", money(deposit_amt)])
    totals_data.append(["BAL ON COMPL", f"{sym}  {balance:,.2f}"])

    totals = Table(totals_data, colWidths=[50 * mm, 40 * mm])
    totals.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 0), (-1, -2), colors.HexColor("#e5e7eb")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d1d5db")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    tagline_text = company.tagline if company and company.tagline else ""
    tagline_para = (
        Paragraph(f"<i><b>{tagline_text}</b></i>", italic_tagline)
        if tagline_text
        else Paragraph("", body)
    )

    tagline_totals = Table(
        [[tagline_para, totals]],
        colWidths=[90 * mm, 90 * mm],
    )
    tagline_totals.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                ("VALIGN", (1, 0), (1, 0), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (1, 0), (1, 0), 0),
            ]
        )
    )
    story.append(tagline_totals)
    story.append(Spacer(1, 4 * mm))

    # ------- 5a. ADDITIONAL NOTES -------
    extras_block = []
    if quotation.additional_notes:
        extras_block.append(Paragraph("<b>ADDITIONAL NOTES</b>", body_sm))
        for line in quotation.additional_notes.splitlines():
            line = line.strip()
            if line:
                extras_block.append(Paragraph(line, body_sm))
        extras_block.append(Spacer(1, 3 * mm))

    # ------- 5. TERMS -------
    balance_pct = Decimal("100") - deposit_pct
    terms_lines = [
        "This is a quotation on the goods named, subject to the conditions noted below:",
        f"This quote may change at any time without prior notice and subject to the standard {company_name} terms and conditions.",
        f"This quote will only be valid once the deposit of {deposit_pct:g}% has been paid.",
        "This quotation will become a contract once accepted and signed by both parties.",
    ]
    terms_block = [Paragraph(line, body_sm) for line in terms_lines]
    terms_block.append(Spacer(1, 3 * mm))
    terms_block.append(Paragraph("<b>Payment arrangement:</b>", body_sm))
    terms_block.append(Paragraph(f"{deposit_pct:g}% ON ACCEPTANCE OF ORDER", body_sm))
    terms_block.append(Paragraph(f"{balance_pct:g}% ON COMPLETION", body_sm))
    terms_block.append(Spacer(1, 3 * mm))
    terms_block.append(Paragraph("To accept this quotation, sign here and return:", body_sm))
    terms_block.append(Spacer(1, 2 * mm))

    # ------- 6. ACCEPTANCE BOX -------
    acceptance = Table(
        [
            [Paragraph("<b>Customer Acceptance</b>", body_sm), "", ""],
            ["", "", ""],
            ["Signature", "Printed Name", "Date"],
        ],
        colWidths=[60 * mm, 60 * mm, 60 * mm],
        rowHeights=[5 * mm, 11 * mm, 5 * mm],
    )
    acceptance.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 1), (-1, 1), 0.6, colors.black),
                ("INNERGRID", (0, 1), (-1, 1), 0.6, colors.black),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#6b7280")),
                ("ALIGN", (0, 2), (-1, 2), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    # Banking
    banking_block = []
    if company and company.bank_details:
        banking_block.append(Spacer(1, 4 * mm))
        banking_block.append(Paragraph("<b>BANKING DETAILS</b>", body_sm))
        for line in company.bank_details.splitlines():
            line = line.strip()
            if line:
                banking_block.append(Paragraph(f"<b>{line}</b>", body_sm))

    # Keep the acceptance box together; allow the rest to flow.
    story.extend(extras_block)
    story.extend(terms_block)
    story.append(KeepTogether(acceptance))
    story.extend(banking_block)

    # ------- Build with footer + continuation header -------
    render_aluflow_pdf(
        doc,
        story,
        continuation_label=f"QUOTATION {quotation.quote_number}",
    )
