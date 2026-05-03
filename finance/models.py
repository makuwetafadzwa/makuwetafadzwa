from decimal import Decimal

from django.db import models
from django.urls import reverse

from core.models import AuditModel


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PARTIALLY_PAID = "partial", "Partially Paid"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class Invoice(AuditModel):
    invoice_number = models.CharField(max_length=30, unique=True, blank=True)
    job = models.ForeignKey(
        "jobs.Job", on_delete=models.PROTECT, related_name="invoices"
    )
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="invoices"
    )
    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("15.00")
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )
    deposit_required = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-issue_date",)

    def __str__(self):
        return self.invoice_number or "Invoice (unsaved)"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("finance:invoice_detail", args=[self.pk])

    @property
    def tax_amount(self):
        taxable = (self.subtotal or Decimal("0")) - (self.discount_amount or Decimal("0"))
        return (taxable * (self.tax_percent or Decimal("0")) / Decimal("100")).quantize(Decimal("0.01"))

    @property
    def total(self):
        return ((self.subtotal or Decimal("0")) - (self.discount_amount or Decimal("0")) + self.tax_amount).quantize(Decimal("0.01"))

    @property
    def paid_amount(self):
        return sum((p.amount for p in self.payments.all()), Decimal("0"))

    @property
    def balance(self):
        return (self.total - self.paid_amount).quantize(Decimal("0.01"))

    @property
    def is_paid(self):
        return self.balance <= Decimal("0")

    def refresh_status(self):
        if self.is_paid:
            self.status = InvoiceStatus.PAID
        elif self.paid_amount > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID
        elif self.status == InvoiceStatus.PAID:
            self.status = InvoiceStatus.ISSUED
        self.save(update_fields=["status", "updated_at"])


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    @property
    def line_total(self):
        return (self.quantity or Decimal("0")) * (self.unit_price or Decimal("0"))


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    BANK_TRANSFER = "bank", "Bank Transfer"
    ECOCASH = "ecocash", "EcoCash"
    CARD = "card", "Card"
    CHEQUE = "cheque", "Cheque"
    OTHER = "other", "Other"


class Payment(AuditModel):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER
    )
    reference = models.CharField(max_length=120, blank=True)
    receipt = models.FileField(upload_to="receipts/", null=True, blank=True)
    notes = models.TextField(blank=True)
    is_deposit = models.BooleanField(default=False)

    class Meta:
        ordering = ("-payment_date",)

    def __str__(self):
        return f"{self.amount} on {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.refresh_status()
