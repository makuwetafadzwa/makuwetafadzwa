from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Role


ROLE_GROUPS = [r.value for r in Role]


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    """Ensure a Django group exists for every role so permissions can attach."""
    if sender.name != "accounts":
        return
    for role in ROLE_GROUPS:
        Group.objects.get_or_create(name=role.title())
