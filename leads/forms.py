from django import forms

from accounts.forms import TailwindMixin
from .models import Lead, LeadActivity


class LeadForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Lead
        exclude = ("created_by", "updated_by", "created_at", "updated_at", "converted_customer")
        widgets = {
            "next_followup": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class LeadActivityForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ("activity_type", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class LeadConvertForm(TailwindMixin, forms.Form):
    create_project = forms.BooleanField(
        required=False, initial=True, label="Create initial project for this customer"
    )
    project_name = forms.CharField(max_length=200, required=False)
    site_address = forms.CharField(max_length=255, required=False)
