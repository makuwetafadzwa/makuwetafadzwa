from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    SALES = "sales", "Sales"
    ESTIMATOR = "estimator", "Estimator"
    INSTALLER = "installer", "Installer"
    STOREKEEPER = "storekeeper", "Storekeeper"
    FINANCE = "finance", "Finance"


class User(AbstractUser):
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.SALES
    )
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    is_active_staff = models.BooleanField(default=True)

    class Meta:
        ordering = ("first_name", "last_name", "username")

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        full = self.get_full_name() or self.username
        parts = [p for p in full.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def has_role(self, *roles):
        return self.is_superuser or self.role in roles
