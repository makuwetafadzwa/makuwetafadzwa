from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsHomeView.as_view(), name="home"),
    path("sales/", views.SalesReportView.as_view(), name="sales"),
    path("jobs/", views.JobsReportView.as_view(), name="jobs"),
    path("finance/", views.FinanceReportView.as_view(), name="finance"),
    path("inventory/", views.InventoryReportView.as_view(), name="inventory"),
]
