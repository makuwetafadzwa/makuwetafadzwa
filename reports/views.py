from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from finance.models import Invoice, InvoiceStatus, Payment, PaymentMethod
from inventory.models import Product, StockMovement
from jobs.models import Job, JobStatus
from leads.models import Lead, LeadStatus
from quotations.models import Quotation


def _date_range(request):
    today = timezone.now().date()
    start = request.GET.get("start") or (today - timedelta(days=30)).isoformat()
    end = request.GET.get("end") or today.isoformat()
    try:
        start_d = date.fromisoformat(start)
    except ValueError:
        start_d = today - timedelta(days=30)
    try:
        end_d = date.fromisoformat(end)
    except ValueError:
        end_d = today
    return start_d, end_d


class ReportsHomeView(LoginRequiredMixin, TemplateView):
    template_name = "reports/home.html"


class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = "reports/sales.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        start, end = _date_range(self.request)
        leads = Lead.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        quotes = Quotation.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        jobs = Job.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        ctx.update({
            "start": start,
            "end": end,
            "lead_count": leads.count(),
            "leads_won": leads.filter(status=LeadStatus.WON).count(),
            "leads_lost": leads.filter(status=LeadStatus.LOST).count(),
            "quote_count": quotes.count(),
            "approved_quotes": quotes.filter(status="approved").count(),
            "approved_value": quotes.filter(status="approved").aggregate(
                total=Sum("items__quantity")
            ),
            "jobs_won_value": jobs.aggregate(total=Sum("contract_value"))["total"] or Decimal("0"),
            "jobs_count": jobs.count(),
            "leads_by_source": leads.values("source").annotate(count=Count("id")),
        })
        return ctx


class JobsReportView(LoginRequiredMixin, TemplateView):
    template_name = "reports/jobs.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        start, end = _date_range(self.request)
        jobs = Job.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        ctx.update({
            "start": start,
            "end": end,
            "jobs": jobs,
            "by_status": jobs.values("status").annotate(
                count=Count("id"), value=Sum("contract_value")
            ),
            "completed": jobs.filter(status=JobStatus.COMPLETED).count(),
            "open": jobs.exclude(status__in=[JobStatus.COMPLETED, JobStatus.CANCELLED]).count(),
            "total_value": jobs.aggregate(total=Sum("contract_value"))["total"] or Decimal("0"),
        })
        return ctx


class FinanceReportView(LoginRequiredMixin, TemplateView):
    template_name = "reports/finance.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        start, end = _date_range(self.request)
        payments = Payment.objects.filter(payment_date__gte=start, payment_date__lte=end)
        invoices = Invoice.objects.filter(issue_date__gte=start, issue_date__lte=end)

        outstanding = Decimal("0")
        for inv in Invoice.objects.exclude(status=InvoiceStatus.CANCELLED):
            outstanding += inv.balance

        ctx.update({
            "start": start,
            "end": end,
            "payments_total": payments.aggregate(total=Sum("amount"))["total"] or Decimal("0"),
            "invoice_count": invoices.count(),
            "invoiced_value": invoices.aggregate(total=Sum("subtotal"))["total"] or Decimal("0"),
            "by_method": payments.values("method").annotate(total=Sum("amount"), count=Count("id")),
            "outstanding": outstanding.quantize(Decimal("0.01")),
            "payment_methods": PaymentMethod.choices,
        })
        return ctx


class InventoryReportView(LoginRequiredMixin, TemplateView):
    template_name = "reports/inventory.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        products = Product.objects.filter(is_active=True)
        low_stock = [p for p in products if p.is_low_stock]
        movements = StockMovement.objects.select_related("product").order_by("-created_at")[:50]
        ctx.update({
            "products": products,
            "low_stock": low_stock,
            "movements": movements,
            "total_skus": products.count(),
            "stock_value": sum(
                ((p.stock_quantity or Decimal("0")) * (p.cost_price or Decimal("0")) for p in products),
                Decimal("0"),
            ),
        })
        return ctx
