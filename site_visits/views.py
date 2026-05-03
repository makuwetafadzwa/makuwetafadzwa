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
from .forms import MeasurementFormSet, SiteVisitForm, SiteVisitImageForm
from .models import SiteVisit, SiteVisitStatus


class SiteVisitListView(LoginRequiredMixin, ListView):
    model = SiteVisit
    template_name = "site_visits/site_visit_list.html"
    context_object_name = "visits"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("customer", "assigned_to")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class SiteVisitDetailView(LoginRequiredMixin, DetailView):
    model = SiteVisit
    template_name = "site_visits/site_visit_detail.html"
    context_object_name = "visit"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["measurements"] = self.object.measurements.all()
        ctx["images"] = self.object.images.all()
        ctx["image_form"] = SiteVisitImageForm()
        return ctx


class SiteVisitCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = SiteVisit
    form_class = SiteVisitForm
    template_name = "site_visits/site_visit_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class SiteVisitUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = SiteVisit
    form_class = SiteVisitForm
    template_name = "site_visits/site_visit_form.html"


class SiteVisitDeleteView(LoginRequiredMixin, DeleteView):
    model = SiteVisit
    template_name = "site_visits/site_visit_confirm_delete.html"
    success_url = reverse_lazy("site_visits:list")


def manage_measurements(request, pk):
    visit = get_object_or_404(SiteVisit, pk=pk)
    if request.method == "POST":
        formset = MeasurementFormSet(request.POST, instance=visit)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                if not obj.pk:
                    obj.created_by = request.user
                obj.updated_by = request.user
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Measurements updated.")
            return redirect(visit.get_absolute_url())
    else:
        formset = MeasurementFormSet(instance=visit)
    return render(
        request,
        "site_visits/measurement_formset.html",
        {"visit": visit, "formset": formset},
    )


def upload_visit_image(request, pk):
    visit = get_object_or_404(SiteVisit, pk=pk)
    if request.method == "POST":
        form = SiteVisitImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.site_visit = visit
            image.created_by = request.user
            image.save()
            messages.success(request, "Image uploaded.")
    return redirect(visit.get_absolute_url())


def mark_completed(request, pk):
    visit = get_object_or_404(SiteVisit, pk=pk)
    visit.status = SiteVisitStatus.COMPLETED
    visit.completed_at = timezone.now()
    visit.updated_by = request.user
    visit.save()
    messages.success(request, "Visit marked as completed.")
    return redirect(visit.get_absolute_url())
