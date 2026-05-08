from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class JobStatus(models.TextChoices):
    CONFIRMED = "confirmed", "Confirmed"
    AWAITING_DEPOSIT = "awaiting_deposit", "Awaiting Deposit"
    SITE_CHECK = "site_check", "Site Check / Re-measure"
    FABRICATION = "fabrication", "Fabrication"
    READY_FOR_INSTALLATION = "ready_install", "Ready for Installation"
    INSTALLED = "installed", "Installed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Job(AuditModel):
    job_number = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=200)
    quotation = models.OneToOneField(
        "quotations.Quotation",
        on_delete=models.PROTECT,
        related_name="job",
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.PROTECT, related_name="jobs"
    )
    project = models.ForeignKey(
        "customers.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    status = models.CharField(
        max_length=30, choices=JobStatus.choices, default=JobStatus.CONFIRMED
    )
    contract_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text="Original quoted price (before any site variations).",
    )
    start_date = models.DateField(null=True, blank=True)
    target_completion = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    assigned_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="jobs", blank=True
    )
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_jobs",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.job_number} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.job_number:
            last = Job.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.job_number = f"JOB-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("jobs:detail", args=[self.pk])

    @property
    def variations_total(self):
        return sum(
            (v.amount for v in self.variations.filter(approved_at__isnull=False)),
            Decimal("0"),
        )

    @property
    def final_value(self):
        """Contract value plus any approved variations."""
        return (self.contract_value + self.variations_total).quantize(Decimal("0.01"))


class JobStatusUpdate(AuditModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="status_updates")
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.job.job_number}: {self.from_status} → {self.to_status}"


class JobVariation(AuditModel):
    """Adjustment to a job's value after the original quote was approved.

    Typically used when the on-site measurements turn out to be larger than
    the plan-based estimate; can also be used for scope changes or discounts.
    """

    REASONS = [
        ("site_larger", "Site measurements larger than plan"),
        ("scope_change", "Scope change requested by customer"),
        ("material_upgrade", "Material upgrade"),
        ("discount", "Discount / goodwill"),
        ("other", "Other"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="variations")
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Positive to charge extra; negative for a refund / discount.",
    )
    reason = models.CharField(max_length=30, choices=REASONS, default="site_larger")
    customer_acknowledged = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_variations",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.job.job_number} variation {self.amount}"

    @property
    def is_approved(self):
        return self.approved_at is not None
