from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import Quotation, QuotationItem


class QuotationForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = (
            "lead",
            "customer",
            "project",
            "issue_date",
            "valid_until",
            "discount_percent",
            "notes",
            "additional_notes",
            "terms",
        )
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "additional_notes": forms.Textarea(attrs={"rows": 4}),
            "terms": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("lead") and not cleaned.get("customer"):
            raise forms.ValidationError(
                "Pick either an existing lead OR an existing customer for this quotation."
            )
        return cleaned


class QuotationItemForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = (
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
