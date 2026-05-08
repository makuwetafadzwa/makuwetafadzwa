"""Auto-log create/update/delete on every model that uses AuditModel.

We attach generic post_save / post_delete handlers to the abstract base.
For UPDATE we diff against the previous DB state captured in pre_save.
"""
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import AuditAction
from .services import log

# Apps whose models should NOT trigger auto-audit (sessions, audit itself,
# anything noisy).
_SKIP_APPS = {"audit", "sessions", "contenttypes", "admin", "auth"}


def _is_audited(sender) -> bool:
    """Decide whether to audit this model. We only audit models that inherit
    from core.models.AuditModel (i.e. business models)."""
    try:
        from core.models import AuditModel
        if AuditModel in sender.__mro__:
            return sender._meta.app_label not in _SKIP_APPS
    except Exception:
        pass
    return False


def _snapshot(instance) -> dict:
    """Return a dict of field values suitable for audit comparison."""
    out = {}
    for f in instance._meta.fields:
        if f.name in ("created_at", "updated_at", "created_by", "updated_by"):
            continue
        try:
            value = getattr(instance, f.attname)
        except Exception:
            value = None
        # Ensure JSON-serialisable
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        elif isinstance(value, (str, int, float, bool, type(None))):
            pass
        else:
            value = str(value)
        out[f.name] = value
    return out


@receiver(pre_save)
def _capture_old(sender, instance, **kwargs):
    if not _is_audited(sender):
        return
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance.__audit_old = _snapshot(old)
        except sender.DoesNotExist:
            instance.__audit_old = None
    else:
        instance.__audit_old = None


@receiver(post_save)
def _on_save(sender, instance, created, **kwargs):
    if not _is_audited(sender):
        return
    new = _snapshot(instance)
    if created:
        log(AuditAction.CREATE, instance, changes=new)
        return
    old = getattr(instance, "__audit_old", None) or {}
    diff = {}
    for k, new_v in new.items():
        if old.get(k) != new_v:
            diff[k] = {"old": old.get(k), "new": new_v}
    if diff:
        log(AuditAction.UPDATE, instance, changes=diff)


@receiver(post_delete)
def _on_delete(sender, instance, **kwargs):
    if not _is_audited(sender):
        return
    log(AuditAction.DELETE, instance, changes=_snapshot(instance))


# ---------- auth signals ----------
@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    log(AuditAction.LOGIN, user, summary=f"{user} logged in")


@receiver(user_logged_out)
def _on_logout(sender, request, user, **kwargs):
    if user:
        log(AuditAction.LOGOUT, user, summary=f"{user} logged out")


@receiver(user_login_failed)
def _on_login_failed(sender, credentials, **kwargs):
    log(
        AuditAction.LOGIN_FAILED,
        target=None,
        summary=f"failed login for {credentials.get('username')}",
        extra={"username": credentials.get("username", "")},
    )
