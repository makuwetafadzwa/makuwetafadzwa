"""Public webhook endpoint for accepting leads from Facebook / WhatsApp /
Zapier / Make.com integrations. Authentication is by a shared API key
configured in settings (ALUFLOW_LEAD_API_KEY).

Wire your channel of choice (e.g. Meta Lead Ads → Zapier → Webhook by Zapier)
to POST JSON like:

    POST /api/leads/webhook/
    Headers: X-Api-Key: <secret>
    Body (JSON):
    {
        "full_name": "Jane Doe",
        "phone": "+263 77 ...",
        "email": "jane@example.com",
        "source": "facebook",
        "product_interest": "windows",
        "notes": "Saw your ad about folding doors.",
        "source_url": "https://wa.me/263771234567/..."
    }
"""
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from leads.models import Lead, LeadSource, LeadStatus, ProductInterest

from .models import AuditAction
from .services import log


VALID_SOURCES = {choice[0] for choice in LeadSource.choices}
VALID_INTERESTS = {choice[0] for choice in ProductInterest.choices}


def _api_key():
    return getattr(settings, "ALUFLOW_LEAD_API_KEY", None) or ""


@csrf_exempt
@require_http_methods(["POST"])
def lead_webhook(request):
    expected = _api_key()
    if not expected:
        return JsonResponse({"error": "Webhook disabled — no API key configured."}, status=503)

    provided = request.headers.get("X-Api-Key") or request.GET.get("api_key", "")
    if provided != expected:
        log(
            AuditAction.LOGIN_FAILED,
            target=None,
            summary="Invalid lead webhook API key",
            extra={"path": request.path},
        )
        return JsonResponse({"error": "Invalid API key."}, status=401)

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    full_name = (payload.get("full_name") or payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    if not full_name or not phone:
        return JsonResponse({"error": "full_name and phone are required."}, status=400)

    source = payload.get("source", LeadSource.OTHER)
    if source not in VALID_SOURCES:
        source = LeadSource.OTHER

    interest = payload.get("product_interest", ProductInterest.OTHER)
    if interest not in VALID_INTERESTS:
        interest = ProductInterest.OTHER

    lead = Lead.objects.create(
        full_name=full_name[:200],
        phone=phone[:30],
        email=(payload.get("email") or "")[:254],
        company=(payload.get("company") or "")[:200],
        address=(payload.get("address") or "")[:255],
        city=(payload.get("city") or "")[:100],
        source=source,
        product_interest=interest,
        status=LeadStatus.NEW,
        notes=payload.get("notes") or "",
        source_url=(payload.get("source_url") or "")[:500],
    )
    log(
        AuditAction.WEBHOOK,
        lead,
        summary=f"Lead created via webhook from {lead.get_source_display()}",
        extra={k: v for k, v in payload.items() if k != "api_key"},
    )
    return JsonResponse(
        {
            "ok": True,
            "id": lead.pk,
            "lead_code": f"LEAD-{lead.pk:05d}",
            "status": lead.status,
        },
        status=201,
    )
