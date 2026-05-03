from django.urls import path

from . import views

app_name = "quotations"

urlpatterns = [
    path("", views.QuotationListView.as_view(), name="list"),
    path("new/", views.QuotationCreateView.as_view(), name="create"),
    path("<int:pk>/", views.QuotationDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.QuotationUpdateView.as_view(), name="edit"),
    path("<int:pk>/items/", views.manage_items, name="items"),
    path("<int:pk>/delete/", views.QuotationDeleteView.as_view(), name="delete"),
    path("<int:pk>/send/", views.mark_sent, name="send"),
    path("<int:pk>/approve/", views.mark_approved, name="approve"),
    path("<int:pk>/reject/", views.mark_rejected, name="reject"),
    path("<int:pk>/revise/", views.revise_quotation, name="revise"),
    path("<int:pk>/pdf/", views.quotation_pdf, name="pdf"),
]
