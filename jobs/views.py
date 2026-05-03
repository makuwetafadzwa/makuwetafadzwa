from decimal import Decimal

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

from core.mixins import AuditMixin
from .forms import JobForm, JobMaterialFormSet, JobStatusForm
from .models import Job, JobStatus, JobStatusUpdate


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
        ctx["materials"] = self.object.materials.select_related("product").all()
        ctx["history"] = self.object.status_updates.all()
        ctx["installations"] = self.object.installations.all() if hasattr(self.object, "installations") else []
        ctx["invoices"] = self.object.invoices.all() if hasattr(self.object, "invoices") else []
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


def manage_materials(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        formset = JobMaterialFormSet(request.POST, instance=job)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.pk:
                    obj.created_by = request.user
                obj.updated_by = request.user
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Bill of materials saved.")
            return redirect(job.get_absolute_url())
    else:
        formset = JobMaterialFormSet(instance=job)
    return render(request, "jobs/job_materials.html", {"job": job, "formset": formset})


def deduct_materials(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.materials_deducted:
        messages.info(request, "Materials already deducted for this job.")
        return redirect(job.get_absolute_url())

    for material in job.materials.all():
        outstanding = (material.quantity_required or Decimal("0")) - (material.quantity_used or Decimal("0"))
        if outstanding > 0:
            material.product.adjust_stock(
                -outstanding,
                reason="job_use",
                user=request.user,
                reference=job.job_number,
            )
            material.quantity_used = material.quantity_required
            material.save()
    job.materials_deducted = True
    job.updated_by = request.user
    job.save()
    messages.success(request, "Materials deducted from inventory.")
    return redirect(job.get_absolute_url())


def update_status(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = JobStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data["status"]
            note = form.cleaned_data.get("note", "")
            JobStatusUpdate.objects.create(
                job=job,
                from_status=job.status,
                to_status=new_status,
                note=note,
                created_by=request.user,
            )
            job.status = new_status
            if new_status == JobStatus.COMPLETED and not job.completed_at:
                job.completed_at = timezone.now().date()
            job.updated_by = request.user
            job.save()
            messages.success(request, f"Job status updated to {job.get_status_display()}.")
    return redirect(job.get_absolute_url())
