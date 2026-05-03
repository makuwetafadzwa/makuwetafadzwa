from decimal import Decimal

from django.conf import settings
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
    quote_number = models.CharField(max_length=30, unique=True, blank=True)
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="quotations"
    )
    project = models.ForeignKey(
        "customers.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations",
    )
    site_visit = models.ForeignKey(
        "site_visits.SiteVisit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versions",
        help_text="Original quote this is a revision of.",
    )
    version = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=QuotationStatus.choices, default=QuotationStatus.DRAFT
    )
    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("15.00"), help_text="VAT %"
    )
    notes = models.TextField(blank=True)
    terms = models.TextField(
        blank=True,
        default=(
            "1. Quote valid for 14 days.\n"
            "2. 50% deposit required to commence work.\n"
            "3. Balance due upon installation completion.\n"
            "4. Lead time 2-4 weeks from deposit confirmation.\n"
        ),
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.quote_number} v{self.version}"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            last = Quotation.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.quote_number = f"QT-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("quotations:detail", args=[self.pk])

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))

    @property
    def discount_amount(self):
        return (self.subtotal * (self.discount_percent or Decimal("0")) / Decimal("100")).quantize(Decimal("0.01"))

    @property
    def taxable_amount(self):
        return self.subtotal - self.discount_amount

    @property
    def tax_amount(self):
        return (self.taxable_amount * (self.tax_percent or Decimal("0")) / Decimal("100")).quantize(Decimal("0.01"))

    @property
    def grand_total(self):
        return (self.taxable_amount + self.tax_amount).quantize(Decimal("0.01"))

    @property
    def is_editable(self):
        return self.status in (QuotationStatus.DRAFT, QuotationStatus.SENT)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "inventory.Product", on_delete=models.SET_NULL, null=True, blank=True
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
