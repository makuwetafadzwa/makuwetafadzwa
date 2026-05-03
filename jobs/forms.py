from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import Job, JobMaterial


class JobForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            "title",
            "customer",
            "project",
            "status",
            "contract_value",
            "start_date",
            "target_completion",
            "completed_at",
            "project_manager",
            "assigned_team",
            "notes",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_completion": forms.DateInput(attrs={"type": "date"}),
            "completed_at": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "assigned_team": forms.SelectMultiple(),
        }


class JobStatusForm(TailwindMixin, forms.Form):
    status = forms.ChoiceField(choices=Job._meta.get_field("status").choices)
    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False)


class JobMaterialForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = JobMaterial
        fields = ("product", "quantity_required", "quantity_used", "notes")


JobMaterialFormSet = inlineformset_factory(
    Job, JobMaterial, form=JobMaterialForm, extra=2, can_delete=True
)
