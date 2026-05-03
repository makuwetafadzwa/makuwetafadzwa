from django.contrib import admin

from .models import Invoice, InvoiceLine, Payment


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "issue_date", "status", "subtotal")
    list_filter = ("status",)
    inlines = [InvoiceLineInline, PaymentInline]
    search_fields = ("invoice_number", "customer__full_name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "payment_date", "amount", "method")
    list_filter = ("method",)
