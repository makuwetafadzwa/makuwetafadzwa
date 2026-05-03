from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)

from .models import User


TAILWIND_INPUT = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-700 shadow-sm focus:border-indigo-500 focus:ring-2 "
    "focus:ring-indigo-200 focus:outline-none"
)


class TailwindMixin:
    """Apply Tailwind classes to all form widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            css = TAILWIND_INPUT
            if isinstance(widget, forms.CheckboxInput):
                css = "h-4 w-4 rounded border-slate-300 text-indigo-600"
            elif isinstance(widget, forms.Select):
                css = TAILWIND_INPUT + " pr-8"
            elif isinstance(widget, forms.Textarea):
                css = TAILWIND_INPUT + " min-h-[90px]"
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = (existing + " " + css).strip()


class LoginForm(TailwindMixin, AuthenticationForm):
    pass


class UserRegistrationForm(TailwindMixin, UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "job_title",
        )


class UserUpdateForm(TailwindMixin, UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "job_title",
            "avatar",
            "is_active",
        )


class ProfileForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "job_title", "avatar")
