from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.LeadListView.as_view(), name="list"),
    path("new/", views.LeadCreateView.as_view(), name="create"),
    path("<int:pk>/", views.LeadDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.LeadUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.LeadDeleteView.as_view(), name="delete"),
    path("<int:pk>/activity/", views.lead_add_activity, name="add_activity"),
    path("<int:pk>/attach/", views.lead_upload_attachment, name="add_attachment"),
    path("<int:pk>/convert/", views.lead_convert_to_customer, name="convert"),
]
