from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class LeadSource(models.TextChoices):
    WHATSAPP = "whatsapp", "WhatsApp"
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    WALK_IN = "walk_in", "Walk-in"
    REFERRAL = "referral", "Referral"
    WEBSITE = "website", "Website"
    PHONE = "phone", "Phone Call"
    EMAIL = "email", "Email"
    OTHER = "other", "Other"


class LeadStatus(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    QUALIFIED = "qualified", "Qualified"
    QUOTED = "quoted", "Quoted"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class ProductInterest(models.TextChoices):
    FOLDING_DOORS = "folding_doors", "Folding Doors"
    SLIDING_DOORS = "sliding_doors", "Sliding Doors"
    WINDOWS = "windows", "Windows"
    SHOWER_DOORS = "shower_doors", "Shower Doors"
    SHOPFRONT = "shopfront", "Shopfront"
    BALUSTRADES = "balustrades", "Balustrades"
    OTHER = "other", "Other"


class Lead(AuditModel):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    source = models.CharField(
        max_length=20, choices=LeadSource.choices, default=LeadSource.WHATSAPP
    )
    source_url = models.URLField(
        blank=True, max_length=500,
        help_text="Original message link, e.g. wa.me/... or m.me/... — for traceability.",
    )
    product_interest = models.CharField(
        max_length=30, choices=ProductInterest.choices, default=ProductInterest.WINDOWS
    )
    status = models.CharField(
        max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW
    )
    estimated_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    next_followup = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    converted_customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_leads",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("leads:detail", args=[self.pk])

    @property
    def lead_code(self):
        return f"LEAD-{self.pk:05d}" if self.pk else "LEAD-?????"

    @property
    def is_won(self):
        return self.status == LeadStatus.WON

    @property
    def is_lost(self):
        return self.status == LeadStatus.LOST

    @property
    def is_converted(self):
        return self.converted_customer_id is not None


class LeadAttachment(AuditModel):
    """Proof-of-source uploads — WhatsApp/Facebook screenshots, voice notes,
    house plan PDFs etc. Required for accountability so a salesperson cannot
    fabricate or hide a lead."""

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="lead_attachments/")
    caption = models.CharField(max_length=200, blank=True)
    KIND_CHOICES = [
        ("screenshot", "Conversation screenshot"),
        ("voice_note", "Voice note"),
        ("house_plan", "House / building plan"),
        ("photo", "Site photo"),
        ("other", "Other"),
    ]
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="screenshot")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.caption or f"Attachment for {self.lead}"


class LeadActivity(AuditModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(
        max_length=30,
        choices=[
            ("call", "Call"),
            ("email", "Email"),
            ("meeting", "Meeting"),
            ("whatsapp", "WhatsApp"),
            ("note", "Note"),
        ],
        default="note",
    )
    description = models.TextField()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_activity_type_display()} on {self.lead}"
