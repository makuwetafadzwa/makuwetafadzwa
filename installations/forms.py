from django import forms

from accounts.forms import TailwindMixin
from .models import Installation, InstallationImage, InstallationTeam


class InstallationForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Installation
        exclude = ("created_by", "updated_by", "created_at", "updated_at", "completed_at")
        widgets = {
            "scheduled_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "completion_notes": forms.Textarea(attrs={"rows": 3}),
        }


class InstallationImageForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = InstallationImage
        fields = ("image", "caption", "is_completion")


class InstallationTeamForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = InstallationTeam
        fields = ("name", "leader", "members")
