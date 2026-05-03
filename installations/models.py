from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import AuditModel


class InstallationStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    SNAGGING = "snagging", "Snagging / Rework"
    CANCELLED = "cancelled", "Cancelled"


class InstallationTeam(AuditModel):
    name = models.CharField(max_length=120, unique=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_install_teams",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="install_teams", blank=True
    )

    def __str__(self):
        return self.name


class Installation(AuditModel):
    job = models.ForeignKey(
        "jobs.Job", on_delete=models.CASCADE, related_name="installations"
    )
    scheduled_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    site_address = models.CharField(max_length=255, blank=True)
    team = models.ForeignKey(
        InstallationTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="installations",
    )
    lead_installer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_installations",
    )
    status = models.CharField(
        max_length=20,
        choices=InstallationStatus.choices,
        default=InstallationStatus.SCHEDULED,
    )
    customer_signoff = models.BooleanField(default=False)
    signoff_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    completion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-scheduled_date",)

    def __str__(self):
        return f"Installation for {self.job.job_number} on {self.scheduled_date:%Y-%m-%d}"

    def get_absolute_url(self):
        return reverse("installations:detail", args=[self.pk])


class InstallationImage(AuditModel):
    installation = models.ForeignKey(
        Installation, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="installations/")
    caption = models.CharField(max_length=200, blank=True)
    is_completion = models.BooleanField(default=False)

    def __str__(self):
        return self.caption or f"Image for {self.installation}"
