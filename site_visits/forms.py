from django import forms
from django.forms import inlineformset_factory

from accounts.forms import TailwindMixin
from .models import Measurement, SiteVisit, SiteVisitImage


class SiteVisitForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = SiteVisit
        exclude = ("created_by", "updated_by", "created_at", "updated_at", "completed_at")
        widgets = {
            "scheduled_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "summary": forms.Textarea(attrs={"rows": 3}),
        }


class MeasurementForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Measurement
        fields = (
            "location_label",
            "product_type",
            "width_mm",
            "height_mm",
            "quantity",
            "glass_type",
            "frame_color",
            "notes",
        )


MeasurementFormSet = inlineformset_factory(
    SiteVisit,
    Measurement,
    form=MeasurementForm,
    extra=2,
    can_delete=True,
)


class SiteVisitImageForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = SiteVisitImage
        fields = ("image", "caption")
