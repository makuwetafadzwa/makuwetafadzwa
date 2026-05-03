from django.contrib import admin

from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quote_number", "version", "customer", "status", "issue_date")
    list_filter = ("status",)
    inlines = [QuotationItemInline]
    search_fields = ("quote_number", "customer__full_name", "customer__company_name")
