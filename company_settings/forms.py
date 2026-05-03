from django import forms

from accounts.forms import TailwindMixin
from .models import CompanyProfile


class CompanyProfileForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = "__all__"
        widgets = {
            "bank_details": forms.Textarea(attrs={"rows": 3}),
        }
