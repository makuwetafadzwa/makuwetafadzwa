from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/new/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdateView.as_view(), name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.InvoiceDeleteView.as_view(), name="invoice_delete"),
    path("invoices/<int:pk>/lines/", views.manage_lines, name="invoice_lines"),
    path("invoices/<int:pk>/issue/", views.issue_invoice, name="invoice_issue"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("invoices/<int:pk>/payment/", views.add_payment, name="add_payment"),
    path("payments/", views.PaymentListView.as_view(), name="payment_list"),
]
