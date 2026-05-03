from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import Invoice, InvoiceLine, Payment


class InvoiceForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        exclude = ("invoice_number", "created_by", "updated_by", "created_at", "updated_at")
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class InvoiceLineForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ("description", "quantity", "unit_price")


InvoiceLineFormSet = inlineformset_factory(
    Invoice, InvoiceLine, form=InvoiceLineForm, extra=2, can_delete=True
)


class PaymentForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("payment_date", "amount", "method", "reference", "receipt", "notes", "is_deposit")
        widgets = {"payment_date": forms.DateInput(attrs={"type": "date"})}
