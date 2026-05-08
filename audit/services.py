"""Helper API for explicit audit log entries from views/services."""
from typing import Any

from .middleware import get_current_ip, get_current_user
from .models import AuditAction, AuditLog


def _actor_label(user):
    if user is None:
        return "system"
    if hasattr(user, "is_anonymous") and user.is_anonymous:
        return "anonymous"
    full = user.get_full_name() if hasattr(user, "get_full_name") else ""
    return full or getattr(user, "username", str(user))


def log(
    action: str,
    target=None,
    *,
    actor=None,
    summary: str = "",
    changes: dict | None = None,
    extra: dict | None = None,
    ip: str | None = None,
):
    """Write an entry to the audit trail.

    `target` can be any model instance (or None for system events).
    """
    user = actor if actor is not None else get_current_user()
    if user is not None and getattr(user, "is_anonymous", False):
        user = None

    if target is not None:
        meta = target._meta
        target_app = meta.app_label
        target_model = meta.model_name
        target_id = str(target.pk) if target.pk is not None else ""
        target_repr = str(target)[:300]
    else:
        target_app = target_model = target_id = target_repr = ""

    return AuditLog.objects.create(
        actor=user if user and getattr(user, "pk", None) else None,
        actor_label=_actor_label(user)[:200],
        action=action,
        target_app=target_app,
        target_model=target_model,
        target_id=target_id,
        target_repr=target_repr,
        summary=summary[:300] if summary else "",
        changes=changes or {},
        extra=extra or {},
        ip_address=ip or get_current_ip(),
    )


# convenience wrappers
def log_create(target, **kw):
    return log(AuditAction.CREATE, target, **kw)


def log_update(target, changes: dict[str, Any] | None = None, **kw):
    return log(AuditAction.UPDATE, target, changes=changes, **kw)


def log_delete(target, **kw):
    return log(AuditAction.DELETE, target, **kw)


def log_status_change(target, from_status: str, to_status: str, note: str = "", **kw):
    return log(
        AuditAction.STATUS_CHANGE,
        target,
        summary=f"{from_status} → {to_status}",
        changes={"status": {"old": from_status, "new": to_status}},
        extra={"note": note} if note else {},
        **kw,
    )
