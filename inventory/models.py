from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class Supplier(AuditModel):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Zimbabwe")
    payment_terms = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("inventory:supplier_detail", args=[self.pk])


class ProductCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Product categories"

    def __str__(self):
        return self.name


class UnitOfMeasure(models.TextChoices):
    EACH = "each", "Each"
    METER = "m", "Meter"
    SQM = "sqm", "Square Meter"
    KG = "kg", "Kilogram"
    LITER = "l", "Liter"
    SHEET = "sheet", "Sheet"
    SET = "set", "Set"


class Product(AuditModel):
    """Product / material catalogue (aluminium profiles, glass, accessories, services)."""

    PRODUCT_KIND = [
        ("material", "Raw Material"),
        ("finished", "Finished Product"),
        ("service", "Service / Labour"),
    ]

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=PRODUCT_KIND, default="material")
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    unit = models.CharField(max_length=10, choices=UnitOfMeasure.choices, default=UnitOfMeasure.EACH)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    preferred_supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.sku} — {self.name}"

    def get_absolute_url(self):
        return reverse("inventory:product_detail", args=[self.pk])

    @property
    def is_low_stock(self):
        if self.kind == "service":
            return False
        return self.stock_quantity <= self.reorder_level

    def adjust_stock(self, delta: Decimal, reason: str, user=None, reference: str = ""):
        """Increase or decrease stock with an audit entry."""
        self.stock_quantity = (self.stock_quantity or Decimal("0")) + Decimal(delta)
        self.save(update_fields=["stock_quantity", "updated_at"])
        StockMovement.objects.create(
            product=self,
            change=Decimal(delta),
            reason=reason,
            reference=reference,
            created_by=user,
        )


class StockMovement(AuditModel):
    REASONS = [
        ("purchase", "Purchase Received"),
        ("job_use", "Job Consumption"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
        ("opening", "Opening Stock"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    change = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASONS)
    reference = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.product.sku} {self.change} ({self.reason})"


class PurchaseOrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ORDERED = "ordered", "Ordered"
    PARTIAL = "partial", "Partially Received"
    RECEIVED = "received", "Received"
    CANCELLED = "cancelled", "Cancelled"


class PurchaseOrder(AuditModel):
    po_number = models.CharField(max_length=30, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PurchaseOrderStatus.choices, default=PurchaseOrderStatus.DRAFT
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-order_date",)

    def __str__(self):
        return f"PO {self.po_number} — {self.supplier}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            last = PurchaseOrder.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.po_number = f"PO-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("inventory:po_detail", args=[self.pk])

    @property
    def total(self):
        return sum((line.line_total for line in self.lines.all()), Decimal("0"))


class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )

    @property
    def line_total(self):
        return (self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))

    @property
    def outstanding(self):
        return (self.quantity or Decimal("0")) - (self.received_quantity or Decimal("0"))
