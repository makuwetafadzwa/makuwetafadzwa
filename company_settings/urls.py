from django.urls import path

from . import views

app_name = "company_settings"

urlpatterns = [
    path("", views.SettingsHomeView.as_view(), name="home"),
    path("company/", views.CompanyProfileView.as_view(), name="company_profile"),
]
