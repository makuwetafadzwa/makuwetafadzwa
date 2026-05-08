"""Audit trail — every meaningful action in Aluflow CRM is recorded here."""
from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "Created"
    UPDATE = "update", "Updated"
    DELETE = "delete", "Deleted"
    STATUS_CHANGE = "status_change", "Status changed"
    APPROVE = "approve", "Approved"
    REJECT = "reject", "Rejected"
    SEND = "send", "Sent"
    PAYMENT = "payment", "Payment recorded"
    LEAD_CONVERTED = "lead_converted", "Lead converted to customer"
    QUOTE_APPROVED = "quote_approved", "Quote approved"
    LOGIN = "login", "Logged in"
    LOGIN_FAILED = "login_failed", "Failed login"
    LOGOUT = "logout", "Logged out"
    WEBHOOK = "webhook", "Created via webhook"
    NOTE = "note", "Note"


class AuditLog(models.Model):
    """A single entry in the audit trail.

    Every entry captures *who*, *what*, *when*, and *what changed*.
    Records that disappear from the parent table are still readable here.
    """

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
    )
    actor_label = models.CharField(
        max_length=200, blank=True,
        help_text="Frozen actor name in case the user is later deleted/renamed.",
    )
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    target_app = models.CharField(max_length=60, blank=True)
    target_model = models.CharField(max_length=60, blank=True)
    target_id = models.CharField(max_length=60, blank=True, db_index=True)
    target_repr = models.CharField(max_length=300, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["target_app", "target_model", "target_id"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self):
        who = self.actor_label or (self.actor.username if self.actor else "system")
        return f"{self.timestamp:%Y-%m-%d %H:%M} · {who} · {self.get_action_display()} · {self.target_repr}"

    @property
    def target_label(self):
        if self.target_app and self.target_model:
            return f"{self.target_app}.{self.target_model}"
        return ""

    @property
    def changed_fields(self):
        return list(self.changes.keys()) if isinstance(self.changes, dict) else []
