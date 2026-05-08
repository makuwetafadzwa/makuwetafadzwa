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

from audit.models import AuditAction, AuditLog
from audit.services import log
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
        qs = super().get_queryset().select_related("customer", "lead", "project")
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["audit_entries"] = AuditLog.objects.filter(
            target_app="quotations", target_model="quotation", target_id=str(self.object.pk)
        ).select_related("actor")[:30]
        return ctx


class QuotationCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotations/quotation_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["issue_date"] = timezone.now().date()
        # If creating from a Lead detail page (?lead=<id>) prefill it
        lead_id = self.request.GET.get("lead")
        if lead_id:
            initial["lead"] = lead_id
        cust_id = self.request.GET.get("customer")
        if cust_id:
            initial["customer"] = cust_id
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
    old = quotation.status
    quotation.status = QuotationStatus.SENT
    quotation.sent_at = timezone.now()
    quotation.updated_by = request.user
    quotation.save()
    log(AuditAction.SEND, quotation, summary=f"Quote sent (was {old})")
    messages.success(request, "Quotation marked as sent.")
    return redirect(quotation.get_absolute_url())


def mark_approved(request, pk):
    """Approving a quotation closes the loop:

    - If the quote is attached to a Lead (no customer yet), convert the
      lead into a Customer first, then attach the quote to that customer.
    - Mark the quote approved + create a Job (handled by signal).
    - Update the lead status to WON.
    """
    quotation = get_object_or_404(Quotation, pk=pk)

    # Auto-convert lead → customer
    if quotation.lead_id and not quotation.customer_id:
        from customers.models import Customer
        from leads.models import LeadStatus

        lead = quotation.lead
        customer = Customer.objects.create(
            full_name=lead.full_name,
            company_name=lead.company,
            phone=lead.phone,
            email=lead.email,
            address_line1=lead.address,
            city=lead.city,
            created_by=request.user,
            updated_by=request.user,
        )
        quotation.customer = customer
        lead.converted_customer = customer
        lead.status = LeadStatus.WON
        lead.save()
        log(
            AuditAction.LEAD_CONVERTED,
            lead,
            summary=f"Lead → customer {customer.customer_code} (via quote approval)",
            extra={"customer_id": customer.pk, "quote_id": quotation.pk},
        )

    quotation.status = QuotationStatus.APPROVED
    quotation.approved_at = timezone.now()
    quotation.updated_by = request.user
    quotation.save()
    log(
        AuditAction.QUOTE_APPROVED,
        quotation,
        summary=f"Quote {quotation.quote_number} approved (value: {quotation.grand_total})",
    )
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
            log(
                AuditAction.REJECT,
                quotation,
                summary="Quote rejected",
                extra={"reason": quotation.rejection_reason},
            )
            messages.success(request, "Quotation marked as rejected.")
            return redirect(quotation.get_absolute_url())
    else:
        form = QuotationRejectForm()
    return render(
        request, "quotations/quotation_reject.html", {"quotation": quotation, "form": form}
    )


def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    buffer = BytesIO()
    build_quotation_pdf(buffer, quotation)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="{quotation.quote_number}.pdf"'
    )
    return response
