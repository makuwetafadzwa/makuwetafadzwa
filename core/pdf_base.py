"""Shared PDF building utilities used by quotation and invoice generators.

Provides:
- ``NumberedCanvas`` — canvas subclass that records every page so we can stamp
  "Page X of Y · Thank you for your business" on every page.
- ``build_aluflow_document`` — common SimpleDocTemplate builder with the
  Aluflow A4 page geometry, continuation-page header callback, and the
  numbered-canvas footer wired in.
- ``COLORS`` and shared paragraph styles.
"""
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate


PAGE_W, PAGE_H = A4
MARGIN_X = 15 * mm
MARGIN_TOP = 12 * mm
MARGIN_BOTTOM = 18 * mm  # extra room for footer


def get_styles():
    """Return a dict of paragraph styles used across PDFs."""
    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["BodyText"], fontSize=9, leading=11, spaceAfter=0)
    return {
        "body": body,
        "body_sm": ParagraphStyle("body_sm", parent=body, fontSize=8.5, leading=11),
        "huge_title": ParagraphStyle(
            "huge_title", parent=body, fontSize=36, leading=40,
            alignment=TA_RIGHT, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#000000"),
        ),
        "label": ParagraphStyle(
            "label", parent=body, fontSize=9, alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        ),
        "value": ParagraphStyle("value", parent=body, fontSize=9, alignment=TA_CENTER),
        "section_header": ParagraphStyle(
            "section_header", parent=body, fontSize=10,
            fontName="Helvetica-Bold", textColor=colors.HexColor("#000000"),
        ),
        "tagline": ParagraphStyle(
            "tagline", parent=body, fontSize=11, alignment=TA_CENTER,
            fontName="Helvetica-BoldOblique",
            textColor=colors.HexColor("#374151"),
        ),
    }


class NumberedCanvas(canvas.Canvas):
    """Canvas that records each page so the footer can show 'Page X of Y'.

    Inspired by the standard ReportLab pattern for total page count rendering.
    """

    def __init__(self, *args, footer_text: str = "Thank you for your business", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []
        self._footer_text = footer_text

    def showPage(self):  # noqa: N802 (reportlab API)
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            super().showPage()
        super().save()

    def _draw_footer(self, total):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6b7280"))
        # Thin separator above the footer
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.4)
        self.line(MARGIN_X, MARGIN_BOTTOM - 4, PAGE_W - MARGIN_X, MARGIN_BOTTOM - 4)
        text = f"Page {self._pageNumber} of {total}"
        if self._footer_text:
            text = f"{text}   ·   {self._footer_text}"
        self.drawCentredString(PAGE_W / 2, MARGIN_BOTTOM - 10, text)
        self.restoreState()


def make_continuation_header(label: str):
    """Return an onLaterPages callback that draws a small "DOC X (continued)"
    line at the very top of pages 2+."""

    def _draw(canv, doc):
        canv.saveState()
        canv.setFont("Helvetica-Bold", 9)
        canv.setFillColor(colors.HexColor("#374151"))
        canv.drawString(MARGIN_X, PAGE_H - 8 * mm, f"{label} (continued)")
        canv.setStrokeColor(colors.HexColor("#9ca3af"))
        canv.setLineWidth(0.4)
        canv.line(MARGIN_X, PAGE_H - 9 * mm, PAGE_W - MARGIN_X, PAGE_H - 9 * mm)
        canv.restoreState()

    return _draw


def build_aluflow_document(buffer, title: str, author: str = "Aluflow"):
    """Return a SimpleDocTemplate with the Aluflow page geometry."""
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=title,
        author=author,
    )


def render_aluflow_pdf(doc, story, continuation_label: str, footer_text: str = "Thank you for your business"):
    """Build the document, wiring the numbered-canvas footer and the
    continuation-page header callback."""

    def canvas_maker(*a, **kw):
        return NumberedCanvas(*a, footer_text=footer_text, **kw)

    doc.build(
        story,
        onLaterPages=make_continuation_header(continuation_label),
        canvasmaker=canvas_maker,
    )


def money(value: Decimal | float | int | None) -> str:
    return f"{Decimal(value or 0):,.2f}"
