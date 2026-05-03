from django.contrib import admin

from .models import Customer, Project


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_code", "display_name", "phone", "email", "customer_type", "city")
    search_fields = ("full_name", "company_name", "phone", "email", "customer_code")
    list_filter = ("customer_type", "city", "country")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "status", "expected_start", "expected_completion")
    list_filter = ("status",)
    search_fields = ("name", "customer__full_name", "customer__company_name")
