from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:home", permanent=False)),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("leads/", include("leads.urls", namespace="leads")),
    path("customers/", include("customers.urls", namespace="customers")),
    path("site-visits/", include("site_visits.urls", namespace="site_visits")),
    path("quotations/", include("quotations.urls", namespace="quotations")),
    path("jobs/", include("jobs.urls", namespace="jobs")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path("installations/", include("installations.urls", namespace="installations")),
    path("finance/", include("finance.urls", namespace="finance")),
    path("reports/", include("reports.urls", namespace="reports")),
    path("settings/", include("company_settings.urls", namespace="company_settings")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
