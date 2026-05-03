from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from finance.models import Invoice, InvoiceStatus, Payment
from inventory.models import Product
from jobs.models import Job, JobStatus
from leads.models import Lead, LeadStatus
from quotations.models import Quotation, QuotationStatus
from site_visits.models import SiteVisit, SiteVisitStatus


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        first_of_month = today.replace(day=1)

        total_leads = Lead.objects.count()
        won_leads = Lead.objects.filter(status=LeadStatus.WON).count()
        conversion_rate = (won_leads / total_leads * 100) if total_leads else 0

        active_jobs = Job.objects.exclude(
            status__in=[JobStatus.COMPLETED, JobStatus.CANCELLED]
        ).count()
        completed_jobs = Job.objects.filter(status=JobStatus.COMPLETED).count()

        revenue_this_month = (
            Payment.objects.filter(payment_date__gte=first_of_month).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0")
        )

        outstanding = Decimal("0")
        for inv in Invoice.objects.exclude(status=InvoiceStatus.CANCELLED):
            outstanding += inv.balance

        low_stock_products = [p for p in Product.objects.filter(is_active=True) if p.is_low_stock][:10]

        recent_leads = Lead.objects.order_by("-created_at")[:5]
        recent_quotes = Quotation.objects.order_by("-created_at")[:5]
        recent_jobs = Job.objects.order_by("-created_at")[:5]
        upcoming_visits = SiteVisit.objects.filter(
            status=SiteVisitStatus.SCHEDULED, scheduled_date__gte=timezone.now()
        ).order_by("scheduled_date")[:5]

        leads_by_status = (
            Lead.objects.values("status").annotate(count=Count("id")).order_by("status")
        )
        leads_by_source = (
            Lead.objects.values("source").annotate(count=Count("id")).order_by("source")
        )

        ctx.update({
            "total_leads": total_leads,
            "won_leads": won_leads,
            "conversion_rate": round(conversion_rate, 1),
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "revenue_this_month": revenue_this_month,
            "outstanding": outstanding.quantize(Decimal("0.01")),
            "low_stock_products": low_stock_products,
            "recent_leads": recent_leads,
            "recent_quotes": recent_quotes,
            "recent_jobs": recent_jobs,
            "upcoming_visits": upcoming_visits,
            "leads_by_status": leads_by_status,
            "leads_by_source": leads_by_source,
            "pending_quotes": Quotation.objects.filter(
                status__in=[QuotationStatus.DRAFT, QuotationStatus.SENT]
            ).count(),
        })
        return ctx
