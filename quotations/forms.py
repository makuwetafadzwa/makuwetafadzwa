from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import Quotation, QuotationItem


class QuotationForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = (
            "customer",
            "project",
            "site_visit",
            "issue_date",
            "valid_until",
            "discount_percent",
            "tax_percent",
            "notes",
            "terms",
        )
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "terms": forms.Textarea(attrs={"rows": 4}),
        }


class QuotationItemForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = (
            "product",
            "description",
            "width_mm",
            "height_mm",
            "quantity",
            "unit_price",
            "sort_order",
        )


QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    form=QuotationItemForm,
    extra=3,
    can_delete=True,
)


class QuotationRejectForm(TailwindMixin, forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
