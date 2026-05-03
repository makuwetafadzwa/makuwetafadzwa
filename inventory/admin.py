from django.contrib import admin

from .models import (
    Product,
    ProductCategory,
    PurchaseOrder,
    PurchaseOrderLine,
    StockMovement,
    Supplier,
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "city")
    search_fields = ("name", "email", "phone")


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "kind", "stock_quantity", "reorder_level", "selling_price")
    list_filter = ("kind", "category")
    search_fields = ("sku", "name")


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("po_number", "supplier", "order_date", "status")
    list_filter = ("status", "order_date")
    inlines = [PurchaseOrderLineInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "change", "reason", "reference", "created_at")
    list_filter = ("reason",)
