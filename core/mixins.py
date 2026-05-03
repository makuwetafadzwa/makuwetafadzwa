from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict a class-based view to one or more roles (or staff/superuser)."""

    allowed_roles: tuple[str, ...] = ()

    def test_func(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return True
        if not self.allowed_roles:
            return True
        return getattr(user, "role", None) in self.allowed_roles


class AuditMixin:
    """Auto-populate created_by and updated_by on form_valid for CBVs."""

    def form_valid(self, form):
        instance = form.save(commit=False)
        if not instance.pk and hasattr(instance, "created_by_id"):
            instance.created_by = self.request.user
        if hasattr(instance, "updated_by_id"):
            instance.updated_by = self.request.user
        instance.save()
        if hasattr(form, "save_m2m"):
            form.save_m2m()
        self.object = instance
        return super().form_valid(form)
