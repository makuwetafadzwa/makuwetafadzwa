from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class SiteVisitStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class SiteVisit(AuditModel):
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.CASCADE, related_name="site_visits"
    )
    project = models.ForeignKey(
        "customers.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="site_visits",
    )
    scheduled_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    site_address = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="site_visits",
    )
    status = models.CharField(
        max_length=20, choices=SiteVisitStatus.choices, default=SiteVisitStatus.SCHEDULED
    )
    notes = models.TextField(blank=True)
    summary = models.TextField(blank=True, help_text="Visit summary written after completion.")

    class Meta:
        ordering = ("-scheduled_date",)

    def __str__(self):
        return f"Visit for {self.customer.display_name} on {self.scheduled_date:%Y-%m-%d}"

    def get_absolute_url(self):
        return reverse("site_visits:detail", args=[self.pk])


class ProductCategory(models.TextChoices):
    FOLDING_DOOR = "folding_door", "Folding Door"
    SLIDING_DOOR = "sliding_door", "Sliding Door"
    HINGED_DOOR = "hinged_door", "Hinged Door"
    WINDOW_CASEMENT = "window_casement", "Casement Window"
    WINDOW_SLIDING = "window_sliding", "Sliding Window"
    WINDOW_TOPHUNG = "window_tophung", "Top Hung Window"
    SHOWER_DOOR = "shower_door", "Shower Door"
    SHOPFRONT = "shopfront", "Shopfront"
    BALUSTRADE = "balustrade", "Balustrade"
    OTHER = "other", "Other"


class Measurement(AuditModel):
    site_visit = models.ForeignKey(
        SiteVisit, on_delete=models.CASCADE, related_name="measurements"
    )
    location_label = models.CharField(
        max_length=120, help_text="e.g. Master bedroom window, Kitchen sliding door"
    )
    product_type = models.CharField(max_length=30, choices=ProductCategory.choices)
    width_mm = models.PositiveIntegerField(help_text="Width in millimetres")
    height_mm = models.PositiveIntegerField(help_text="Height in millimetres")
    quantity = models.PositiveIntegerField(default=1)
    glass_type = models.CharField(max_length=120, blank=True)
    frame_color = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.location_label} ({self.width_mm}x{self.height_mm}mm)"

    @property
    def area_sqm(self):
        return round((self.width_mm * self.height_mm) / 1_000_000, 3)


class SiteVisitImage(AuditModel):
    site_visit = models.ForeignKey(
        SiteVisit, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="site_visits/")
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.caption or f"Image for {self.site_visit}"
