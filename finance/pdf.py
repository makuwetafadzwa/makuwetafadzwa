"""PDF generation for invoices using ReportLab.

Mirrors the Aluflow quotation PDF style — logo + address top-left, big
INVOICE + meta table top-right, customer info bar, itemised table,
totals stack with paid / balance, payment instructions, and banking
details. Multi-page invoices are supported with a repeating column
header and a "INVOICE <number> (continued)" line on subsequent pages.
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


def build_invoice_pdf(buffer, invoice):
    from company_settings.models import CompanyProfile

    company = CompanyProfile.objects.first()
    sym = company.currency_symbol if company else "$"
    company_name = company.name if company else "Aluflow"

    doc = build_aluflow_document(
        buffer,
        title=f"Invoice {invoice.invoice_number}",
        author=company_name,
    )

    s = get_styles()
    body, body_sm = s["body"], s["body_sm"]
    huge_title = s["huge_title"]
    label, value = s["label"], s["value"]
    section_header = s["section_header"]
    italic_tagline = s["tagline"]

    story = []

    # ------- 1. HEADER -------
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
        if company.tax_number:
            addr_lines.append(f"Tax No: {company.tax_number}")
    if addr_lines:
        left_cell.append(Paragraph("<br/>".join(addr_lines), body_sm))

    invoice_word = Paragraph("INVOICE", huge_title)
    due = invoice.due_date.strftime("%d/%m/%Y") if invoice.due_date else "—"
    meta_table = Table(
        [
            [Paragraph("INVOICE #", label), Paragraph("DATE", label)],
            [
                Paragraph(invoice.invoice_number, value),
                Paragraph(invoice.issue_date.strftime("%d/%m/%Y"), value),
            ],
            [Paragraph("CUSTOMER ID", label), Paragraph("DUE DATE", label)],
            [
                Paragraph(invoice.customer.customer_code or "", value),
                Paragraph(due, value),
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
        [[left_cell, [invoice_word, Spacer(1, 4 * mm), meta_table]]],
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

    # ------- 2. CUSTOMER INFO + JOB REF -------
    cust = invoice.customer
    customer_header = Table(
        [[Paragraph("BILL TO", section_header)]],
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

    cust_lines = [cust.full_name]
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
    if cust.tax_number:
        cust_lines.append(f"Tax No: {cust.tax_number}")
    contact_bits = " · ".join(filter(None, [cust.phone, cust.email]))
    if contact_bits:
        cust_lines.append(contact_bits)
    customer_text = Paragraph("<br/>".join(cust_lines), body_sm)

    job_ref = invoice.job.job_number if invoice.job else "—"
    status_label = invoice.get_status_display().upper()
    status_colour = {
        "PAID": "#10b981",
        "PARTIALLY PAID": "#f59e0b",
        "OVERDUE": "#ef4444",
        "ISSUED": "#3b82f6",
        "DRAFT": "#6b7280",
        "CANCELLED": "#6b7280",
    }.get(status_label, "#374151")
    status_para = Paragraph(
        f'<font color="{status_colour}"><b>{status_label}</b></font>',
        body_sm,
    )
    right_block = Paragraph(
        f"<i>Job:</i> <b>{job_ref}</b><br/><i>Status:</i> ", body_sm
    )

    cust_row = Table(
        [
            [
                [customer_header, Spacer(1, 3 * mm), customer_text],
                [Spacer(1, 12 * mm), right_block, status_para],
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

    # ------- 3. ITEMS TABLE -------
    lines = list(invoice.lines.all())
    rows = [["DESCRIPTION", "QTY", "UNIT PRICE", "AMOUNT"]]
    for line in lines:
        rows.append(
            [
                Paragraph(line.description, body_sm),
                f"{line.quantity:g}",
                money(line.unit_price),
                money(line.line_total),
            ]
        )
    if len(lines) <= 4:
        for _ in range(max(0, 4 - len(lines))):
            rows.append(["", "", "", ""])

    items_table = Table(
        rows,
        colWidths=[100 * mm, 20 * mm, 30 * mm, 30 * mm],
        repeatRows=1,
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d1d5db")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
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

    # ------- 4. TAGLINE + TOTALS (with paid/balance) -------
    paid = invoice.paid_amount
    balance = invoice.balance

    totals_data = [["SUBTOTAL", money(invoice.subtotal)]]
    if invoice.discount_amount > 0:
        totals_data.append(["DISCOUNT", "-" + money(invoice.discount_amount)])
    if invoice.tax_amount > 0:
        totals_data.append([f"VAT ({invoice.tax_percent:g}%)", money(invoice.tax_amount)])
    totals_data.append(["TOTAL", money(invoice.total)])
    totals_data.append(["PAID", money(paid)])
    totals_data.append(["BALANCE DUE", f"{sym}  {balance:,.2f}"])

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
                ("TEXTCOLOR", (0, -2), (-1, -2), colors.HexColor("#10b981")),
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

    # ------- 5. PAYMENT INSTRUCTIONS / NOTES -------
    body_block = []
    if invoice.notes:
        body_block.append(Paragraph("<b>NOTES</b>", body_sm))
        for line in invoice.notes.splitlines():
            line = line.strip()
            if line:
                body_block.append(Paragraph(line, body_sm))
        body_block.append(Spacer(1, 3 * mm))

    body_block.append(
        Paragraph(
            "Please reference the invoice number above when making payment. "
            "Thank you for your business — we look forward to serving you again.",
            body_sm,
        )
    )

    # ------- 6. BANKING DETAILS -------
    if company and company.bank_details:
        body_block.append(Spacer(1, 4 * mm))
        body_block.append(Paragraph("<b>BANKING DETAILS</b>", body_sm))
        for line in company.bank_details.splitlines():
            line = line.strip()
            if line:
                body_block.append(Paragraph(f"<b>{line}</b>", body_sm))

    story.append(KeepTogether(body_block))

    # ------- Build with footer + continuation header -------
    render_aluflow_pdf(
        doc,
        story,
        continuation_label=f"INVOICE {invoice.invoice_number}",
    )
