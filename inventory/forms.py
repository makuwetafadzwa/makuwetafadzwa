from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import (
    Product,
    ProductCategory,
    PurchaseOrder,
    PurchaseOrderLine,
    Supplier,
)


class SupplierForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ("created_by", "updated_by", "created_at", "updated_at")


class ProductForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("created_by", "updated_by", "created_at", "updated_at")


class ProductCategoryForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ("name", "description")


class PurchaseOrderForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        exclude = ("po_number", "created_by", "updated_by", "created_at", "updated_at")
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_date": forms.DateInput(attrs={"type": "date"}),
        }


class PurchaseOrderLineForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ("product", "quantity", "unit_cost", "received_quantity")


PurchaseOrderLineFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderLine,
    form=PurchaseOrderLineForm,
    extra=2,
    can_delete=True,
)


class StockAdjustmentForm(TailwindMixin, forms.Form):
    change = forms.DecimalField(max_digits=12, decimal_places=2)
    reason = forms.ChoiceField(
        choices=[
            ("adjustment", "Adjustment"),
            ("opening", "Opening Stock"),
            ("return", "Return"),
        ]
    )
    reference = forms.CharField(max_length=120, required=False)
