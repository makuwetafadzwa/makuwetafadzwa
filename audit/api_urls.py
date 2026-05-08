"""Public API endpoints (audited) — currently the lead webhook only."""
from django.urls import path

from . import api_views

app_name = "audit_api"

urlpatterns = [
    path("leads/webhook/", api_views.lead_webhook, name="lead_webhook"),
]
