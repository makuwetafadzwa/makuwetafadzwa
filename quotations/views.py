from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
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
from .forms import QuotationForm, QuotationItemFormSet, QuotationRejectForm
from .models import Quotation, QuotationStatus
from .pdf import build_quotation_pdf


class QuotationListView(LoginRequiredMixin, ListView):
    model = Quotation
    template_name = "quotations/quotation_list.html"
    context_object_name = "quotations"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("customer", "project")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = QuotationStatus.choices
        return ctx


class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = "quotations/quotation_detail.html"
    context_object_name = "quotation"


class QuotationCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotations/quotation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["issue_date"] = timezone.now().date()
        return initial

    def get_success_url(self):
        return reverse_lazy("quotations:items", args=[self.object.pk])


class QuotationUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotations/quotation_form.html"

    def get_success_url(self):
        return reverse_lazy("quotations:detail", args=[self.object.pk])


class QuotationDeleteView(LoginRequiredMixin, DeleteView):
    model = Quotation
    template_name = "quotations/quotation_confirm_delete.html"
    success_url = reverse_lazy("quotations:list")


def manage_items(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if not quotation.is_editable:
        messages.warning(request, "Quotation can no longer be edited.")
        return redirect(quotation.get_absolute_url())

    if request.method == "POST":
        formset = QuotationItemFormSet(request.POST, instance=quotation)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Quotation items saved.")
            return redirect(quotation.get_absolute_url())
    else:
        formset = QuotationItemFormSet(instance=quotation)
    return render(
        request,
        "quotations/quotation_items.html",
        {"quotation": quotation, "formset": formset},
    )


def mark_sent(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    quotation.status = QuotationStatus.SENT
    quotation.sent_at = timezone.now()
    quotation.updated_by = request.user
    quotation.save()
    messages.success(request, "Quotation marked as sent.")
    return redirect(quotation.get_absolute_url())


def mark_approved(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    quotation.status = QuotationStatus.APPROVED
    quotation.approved_at = timezone.now()
    quotation.updated_by = request.user
    quotation.save()
    messages.success(request, "Quotation approved. A job has been created.")
    return redirect(quotation.get_absolute_url())


def mark_rejected(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        form = QuotationRejectForm(request.POST)
        if form.is_valid():
            quotation.status = QuotationStatus.REJECTED
            quotation.rejected_at = timezone.now()
            quotation.rejection_reason = form.cleaned_data.get("reason", "")
            quotation.updated_by = request.user
            quotation.save()
            messages.success(request, "Quotation marked as rejected.")
            return redirect(quotation.get_absolute_url())
    else:
        form = QuotationRejectForm()
    return render(
        request, "quotations/quotation_reject.html", {"quotation": quotation, "form": form}
    )


def revise_quotation(request, pk):
    original = get_object_or_404(Quotation, pk=pk)
    base = original.parent or original
    last_version = (
        Quotation.objects.filter(parent=base).order_by("-version").first()
    )
    new_version_number = (last_version.version + 1) if last_version else (base.version + 1)

    new_q = Quotation.objects.create(
        customer=original.customer,
        project=original.project,
        site_visit=original.site_visit,
        parent=base,
        version=new_version_number,
        status=QuotationStatus.DRAFT,
        issue_date=timezone.now().date(),
        valid_until=original.valid_until,
        discount_percent=original.discount_percent,
        tax_percent=original.tax_percent,
        notes=original.notes,
        terms=original.terms,
        created_by=request.user,
        updated_by=request.user,
    )
    for item in original.items.all():
        item.pk = None
        item.quotation = new_q
        item.save()

    messages.success(request, f"Created new quotation version {new_version_number}.")
    return redirect(new_q.get_absolute_url())


def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    buffer = BytesIO()
    build_quotation_pdf(buffer, quotation)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="{quotation.quote_number}-v{quotation.version}.pdf"'
    )
    return response
