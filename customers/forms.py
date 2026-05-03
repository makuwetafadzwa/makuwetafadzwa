from django import forms

from accounts.forms import TailwindMixin
from .models import Customer, Project


class CustomerForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ("customer_code", "created_by", "updated_by", "created_at", "updated_at")


class ProjectForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Project
        exclude = ("created_by", "updated_by", "created_at", "updated_at")
        widgets = {
            "expected_start": forms.DateInput(attrs={"type": "date"}),
            "expected_completion": forms.DateInput(attrs={"type": "date"}),
        }
