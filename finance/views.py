from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
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
from jobs.models import Job
from .forms import InvoiceForm, InvoiceLineFormSet, PaymentForm
from .models import Invoice, InvoiceStatus, Payment


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "finance/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        outstanding = Decimal("0")
        for inv in Invoice.objects.exclude(status=InvoiceStatus.CANCELLED):
            outstanding += inv.balance
        ctx["total_outstanding"] = outstanding
        ctx["statuses"] = InvoiceStatus.choices
        return ctx


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "finance/invoice_detail.html"
    context_object_name = "invoice"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["payment_form"] = PaymentForm(initial={"payment_date": timezone.now().date()})
        return ctx


class InvoiceCreateView(LoginRequiredMixin, AuditMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["issue_date"] = timezone.now().date()
        job_id = self.request.GET.get("job")
        if job_id:
            try:
                job = Job.objects.get(pk=job_id)
                initial["job"] = job.id
                initial["customer"] = job.customer_id
                initial["subtotal"] = job.contract_value
            except Job.DoesNotExist:
                pass
        return initial

    def get_success_url(self):
        return reverse_lazy("finance:invoice_lines", args=[self.object.pk])


class InvoiceUpdateView(LoginRequiredMixin, AuditMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = "finance/invoice_confirm_delete.html"
    success_url = reverse_lazy("finance:invoice_list")


def manage_lines(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        formset = InvoiceLineFormSet(request.POST, instance=invoice)
        if formset.is_valid():
            formset.save()
            invoice.subtotal = sum(
                (line.line_total for line in invoice.lines.all()), Decimal("0")
            )
            invoice.save(update_fields=["subtotal", "updated_at"])
            messages.success(request, "Invoice lines saved.")
            return redirect(invoice.get_absolute_url())
    else:
        formset = InvoiceLineFormSet(instance=invoice)
    return render(request, "finance/invoice_lines.html", {"invoice": invoice, "formset": formset})


def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.invoice = invoice
            p.created_by = request.user
            p.save()
            messages.success(request, f"Payment of {p.amount} recorded.")
    return redirect(invoice.get_absolute_url())


def issue_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = InvoiceStatus.ISSUED
    invoice.updated_by = request.user
    invoice.save(update_fields=["status", "updated_at"])
    messages.success(request, "Invoice issued.")
    return redirect(invoice.get_absolute_url())


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "finance/payment_list.html"
    context_object_name = "payments"
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related("invoice", "invoice__customer")
