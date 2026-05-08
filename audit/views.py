from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from accounts.models import Role
from core.mixins import RoleRequiredMixin
from .models import AuditAction, AuditLog


class AuditLogView(RoleRequiredMixin, ListView):
    model = AuditLog
    template_name = "audit/log_list.html"
    context_object_name = "entries"
    paginate_by = 50
    allowed_roles = (Role.ADMIN, Role.MANAGER)

    def get_queryset(self):
        qs = super().get_queryset().select_related("actor")
        q = self.request.GET.get("q")
        action = self.request.GET.get("action")
        actor_id = self.request.GET.get("actor")
        model = self.request.GET.get("model")
        if q:
            qs = qs.filter(
                Q(target_repr__icontains=q)
                | Q(summary__icontains=q)
                | Q(actor_label__icontains=q)
            )
        if action:
            qs = qs.filter(action=action)
        if actor_id:
            qs = qs.filter(actor_id=actor_id)
        if model:
            qs = qs.filter(target_model=model)
        return qs

    def get_context_data(self, **kwargs):
        from accounts.models import User
        ctx = super().get_context_data(**kwargs)
        ctx["actions"] = AuditAction.choices
        ctx["users"] = User.objects.order_by("first_name", "username")
        ctx["models"] = (
            AuditLog.objects.values_list("target_model", flat=True)
            .exclude(target_model="")
            .distinct()
        )
        return ctx


class AuditLogDetailView(RoleRequiredMixin, DetailView):
    model = AuditLog
    template_name = "audit/log_detail.html"
    context_object_name = "entry"
    allowed_roles = (Role.ADMIN, Role.MANAGER)
