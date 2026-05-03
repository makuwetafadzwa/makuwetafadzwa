from django.urls import path

from . import views

app_name = "site_visits"

urlpatterns = [
    path("", views.SiteVisitListView.as_view(), name="list"),
    path("new/", views.SiteVisitCreateView.as_view(), name="create"),
    path("<int:pk>/", views.SiteVisitDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.SiteVisitUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.SiteVisitDeleteView.as_view(), name="delete"),
    path("<int:pk>/measurements/", views.manage_measurements, name="measurements"),
    path("<int:pk>/upload-image/", views.upload_visit_image, name="upload_image"),
    path("<int:pk>/complete/", views.mark_completed, name="complete"),
]
