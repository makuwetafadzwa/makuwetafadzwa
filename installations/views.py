from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.mixins import AuditMixin
from jobs.models import Job, JobStatus
from .forms import InstallationForm, InstallationImageForm, InstallationTeamForm
from .models import Installation, InstallationStatus, InstallationTeam


class InstallationListView(LoginRequiredMixin, ListView):
    model = Installation
    template_name = "installations/installation_list.html"
    context_object_name = "installations"
    paginate_by = 20


class InstallationDetailView(LoginRequiredMixin, DetailView):
    model = Installation
    template_name = "installations/installation_detail.html"
    context_object_name = "installation"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["images"] = self.object.images.all()
        ctx["image_form"] = InstallationImageForm()
        return ctx


class InstallationCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Installation
    form_class = InstallationForm
    template_name = "installations/installation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        job_id = self.request.GET.get("job")
        if job_id:
            initial["job"] = job_id
        return initial

    def get_success_url(self):
        return self.object.get_absolute_url()


class InstallationUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Installation
    form_class = InstallationForm
    template_name = "installations/installation_form.html"


class InstallationDeleteView(LoginRequiredMixin, DeleteView):
    model = Installation
    template_name = "installations/installation_confirm_delete.html"
    success_url = reverse_lazy("installations:list")


def upload_image(request, pk):
    install = get_object_or_404(Installation, pk=pk)
    if request.method == "POST":
        form = InstallationImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.installation = install
            img.created_by = request.user
            img.save()
            messages.success(request, "Image uploaded.")
    return redirect(install.get_absolute_url())


def mark_completed(request, pk):
    install = get_object_or_404(Installation, pk=pk)
    install.status = InstallationStatus.COMPLETED
    install.completed_at = timezone.now()
    install.updated_by = request.user
    install.save()

    job = install.job
    job.status = JobStatus.INSTALLED
    job.updated_by = request.user
    job.save()
    messages.success(request, "Installation marked complete; job set to Installed.")
    return redirect(install.get_absolute_url())


# --------------- Teams ---------------
class TeamListView(LoginRequiredMixin, ListView):
    model = InstallationTeam
    template_name = "installations/team_list.html"
    context_object_name = "teams"


class TeamCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = InstallationTeam
    form_class = InstallationTeamForm
    template_name = "installations/team_form.html"
    success_url = reverse_lazy("installations:team_list")


class TeamUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = InstallationTeam
    form_class = InstallationTeamForm
    template_name = "installations/team_form.html"
    success_url = reverse_lazy("installations:team_list")


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = InstallationTeam
    template_name = "installations/team_confirm_delete.html"
    success_url = reverse_lazy("installations:team_list")
