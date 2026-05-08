from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.JobListView.as_view(), name="list"),
    path("new/", views.JobCreateView.as_view(), name="create"),
    path("<int:pk>/", views.JobDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.JobUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.JobDeleteView.as_view(), name="delete"),
    path("<int:pk>/status/", views.update_status, name="status"),
    path("<int:pk>/variation/", views.add_variation, name="add_variation"),
    path("variations/<int:pk>/approve/", views.approve_variation, name="approve_variation"),
]
