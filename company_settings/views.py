from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from accounts.models import Role
from core.mixins import RoleRequiredMixin
from .forms import CompanyProfileForm
from .models import CompanyProfile


class SettingsHomeView(RoleRequiredMixin, TemplateView):
    template_name = "company_settings/home.html"
    allowed_roles = (Role.ADMIN, Role.MANAGER)


class CompanyProfileView(RoleRequiredMixin, TemplateView):
    template_name = "company_settings/company_profile.html"
    allowed_roles = (Role.ADMIN, Role.MANAGER)

    def get(self, request, *args, **kwargs):
        profile = CompanyProfile.get_solo()
        form = CompanyProfileForm(instance=profile)
        return render(request, self.template_name, {"form": form, "profile": profile})

    def post(self, request, *args, **kwargs):
        profile = CompanyProfile.get_solo()
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated.")
            return redirect("company_settings:company_profile")
        return render(request, self.template_name, {"form": form, "profile": profile})
