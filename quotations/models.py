from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class QuotationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"


class Quotation(AuditModel):
    """A quote can be issued to either a Lead (rough quote from plans) or
    a Customer (existing relationship). Exactly one of the two is required.
    Approval converts a lead-quote: the lead is converted into a customer
    and a Job is auto-created via signals.
    """

    quote_number = models.CharField(max_length=30, unique=True, blank=True)
    lead = models.ForeignKey(
        "leads.Lead",
        on_delete=models.PROTECT,
        related_name="quotations",
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="quotations",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        "customers.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations",
    )
    status = models.CharField(
        max_length=20, choices=QuotationStatus.choices, default=QuotationStatus.DRAFT
    )
    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    notes = models.TextField(
        blank=True,
        help_text="Visible to customer on the PDF (under the items table).",
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Extra clauses, scope details or assumptions printed before the terms.",
    )
    terms = models.TextField(
        blank=True,
        default=(
            "1. Quote valid for 14 days from issue.\n"
            "2. 75% deposit required on acceptance.\n"
            "3. 25% balance due on completion of installation.\n"
            "4. Lead time 2–4 weeks from deposit confirmation.\n"
            "5. Final pricing subject to on-site verification of measurements; any "
            "increase will be communicated and approved before fabrication.\n"
        ),
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.quote_number or "Quotation (unsaved)"

    def clean(self):
        super().clean()
        if not self.lead_id and not self.customer_id:
            raise ValidationError(
                "A quotation must reference either a lead or an existing customer."
            )

    def save(self, *args, **kwargs):
        if not self.quote_number:
            last = Quotation.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.quote_number = f"QT-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("quotations:detail", args=[self.pk])

    # ---------- Recipient helpers (lead OR customer) ----------
    @property
    def recipient_name(self):
        if self.customer_id:
            return self.customer.display_name
        if self.lead_id:
            return self.lead.full_name
        return ""

    @property
    def recipient_phone(self):
        if self.customer_id:
            return self.customer.phone
        if self.lead_id:
            return self.lead.phone
        return ""

    @property
    def recipient_email(self):
        if self.customer_id:
            return self.customer.email
        if self.lead_id:
            return self.lead.email
        return ""

    @property
    def recipient_address(self):
        if self.customer_id:
            return self.customer.address_line1 or ""
        if self.lead_id:
            return self.lead.address or ""
        return ""

    @property
    def recipient_code(self):
        if self.customer_id:
            return self.customer.customer_code or ""
        if self.lead_id:
            return f"LEAD-{self.lead_id:05d}"
        return ""

    # ---------- Totals ----------
    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))

    @property
    def discount_amount(self):
        return (self.subtotal * (self.discount_percent or Decimal("0")) / Decimal("100")).quantize(Decimal("0.01"))

    @property
    def grand_total(self):
        return (self.subtotal - self.discount_amount).quantize(Decimal("0.01"))

    # ---------- Status helpers ----------
    @property
    def is_editable(self):
        return self.status in (QuotationStatus.DRAFT, QuotationStatus.SENT)

    @property
    def is_lead_quote(self):
        return self.lead_id is not None and self.customer_id is None


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name="items"
    )
    description = models.CharField(max_length=255)
    width_mm = models.PositiveIntegerField(null=True, blank=True)
    height_mm = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))
