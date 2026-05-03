from django.db import models
from django.urls import reverse

from core.models import AuditModel


class CustomerType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    COMPANY = "company", "Company"
    GOVERNMENT = "government", "Government"
    DEVELOPER = "developer", "Property Developer"


class Customer(AuditModel):
    customer_code = models.CharField(max_length=20, unique=True, blank=True)
    customer_type = models.CharField(
        max_length=20, choices=CustomerType.choices, default=CustomerType.INDIVIDUAL
    )
    full_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    alt_phone = models.CharField(max_length=30, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Zimbabwe")
    tax_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        if self.customer_type != CustomerType.INDIVIDUAL and self.company_name:
            return self.company_name
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.customer_code:
            last = Customer.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.customer_code = f"CUST-{next_id:05d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("customers:detail", args=[self.pk])


class Project(AuditModel):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    site_address = models.CharField(max_length=255, blank=True)
    site_city = models.CharField(max_length=100, blank=True)
    expected_start = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="planning"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} ({self.customer.display_name})"

    def get_absolute_url(self):
        return reverse("customers:project_detail", args=[self.pk])
