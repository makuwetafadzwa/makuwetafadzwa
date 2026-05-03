from decimal import Decimal

from django.db import models


class CompanyProfile(models.Model):
    name = models.CharField(max_length=200, default="Aluflow Glass & Aluminium")
    tagline = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to="branding/", null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Zimbabwe")
    tax_number = models.CharField(max_length=50, blank=True)
    bank_details = models.TextField(blank=True)
    default_vat_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("15.00")
    )
    currency_symbol = models.CharField(max_length=5, default="$")
    currency_code = models.CharField(max_length=10, default="USD")

    class Meta:
        verbose_name = "Company profile"
        verbose_name_plural = "Company profile"

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
