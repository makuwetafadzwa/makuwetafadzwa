from django.urls import path

from . import views

app_name = "installations"

urlpatterns = [
    path("", views.InstallationListView.as_view(), name="list"),
    path("new/", views.InstallationCreateView.as_view(), name="create"),
    path("<int:pk>/", views.InstallationDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.InstallationUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.InstallationDeleteView.as_view(), name="delete"),
    path("<int:pk>/upload/", views.upload_image, name="upload_image"),
    path("<int:pk>/complete/", views.mark_completed, name="complete"),

    path("teams/", views.TeamListView.as_view(), name="team_list"),
    path("teams/new/", views.TeamCreateView.as_view(), name="team_create"),
    path("teams/<int:pk>/edit/", views.TeamUpdateView.as_view(), name="team_edit"),
    path("teams/<int:pk>/delete/", views.TeamDeleteView.as_view(), name="team_delete"),
]
