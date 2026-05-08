from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from audit.models import AuditAction, AuditLog
from audit.services import log, log_status_change
from core.mixins import AuditMixin
from .forms import JobForm, JobStatusForm, JobVariationForm
from .models import Job, JobStatus, JobStatusUpdate, JobVariation


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "jobs/job_list.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("customer", "project")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = JobStatus.choices
        return ctx


class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_form"] = JobStatusForm(initial={"status": self.object.status})
        ctx["variation_form"] = JobVariationForm()
        ctx["variations"] = self.object.variations.select_related("approved_by").all()
        ctx["history"] = self.object.status_updates.all()
        ctx["installations"] = (
            self.object.installations.all() if hasattr(self.object, "installations") else []
        )
        ctx["invoices"] = (
            self.object.invoices.all() if hasattr(self.object, "invoices") else []
        )
        ctx["audit_entries"] = AuditLog.objects.filter(
            target_app="jobs", target_model="job", target_id=str(self.object.pk)
        ).select_related("actor")[:30]
        return ctx


class JobCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class JobUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = "jobs/job_confirm_delete.html"
    success_url = reverse_lazy("jobs:list")


def update_status(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = JobStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data["status"]
            note = form.cleaned_data.get("note", "")
            old_status = job.status
            JobStatusUpdate.objects.create(
                job=job,
                from_status=old_status,
                to_status=new_status,
                note=note,
                created_by=request.user,
            )
            job.status = new_status
            if new_status == JobStatus.COMPLETED and not job.completed_at:
                job.completed_at = timezone.now().date()
            job.updated_by = request.user
            job.save()
            log_status_change(job, old_status, new_status, note=note)
            messages.success(request, f"Job status updated to {job.get_status_display()}.")
    return redirect(job.get_absolute_url())


def add_variation(request, pk):
    """Record a price change after the original quote was approved
    (e.g. site measurements were larger than the plan-based estimate)."""
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = JobVariationForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.job = job
            v.created_by = request.user
            v.updated_by = request.user
            v.save()
            log(
                AuditAction.NOTE,
                v,
                summary=f"Variation logged on {job.job_number}: {v.amount}",
                extra={"reason": v.reason, "job_id": job.pk},
            )
            messages.success(request, "Variation recorded. Awaiting manager approval.")
    return redirect(job.get_absolute_url())


def approve_variation(request, pk):
    variation = get_object_or_404(JobVariation, pk=pk)
    if variation.is_approved:
        messages.info(request, "This variation has already been approved.")
        return redirect(variation.job.get_absolute_url())
    variation.approved_at = timezone.now()
    variation.approved_by = request.user
    variation.updated_by = request.user
    variation.save()
    log(
        AuditAction.APPROVE,
        variation,
        summary=f"Variation approved: {variation.amount} on {variation.job.job_number}",
    )
    messages.success(request, "Variation approved and applied to the job total.")
    return redirect(variation.job.get_absolute_url())
