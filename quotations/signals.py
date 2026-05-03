from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Quotation, QuotationStatus


@receiver(post_save, sender=Quotation)
def auto_create_job_on_approval(sender, instance, created, **kwargs):
    """When a quotation is approved, automatically create a Job linked to it."""
    if created:
        return
    if instance.status != QuotationStatus.APPROVED:
        return

    from jobs.models import Job, JobStatus

    if Job.objects.filter(quotation=instance).exists():
        return

    Job.objects.create(
        quotation=instance,
        customer=instance.customer,
        project=instance.project,
        status=JobStatus.CONFIRMED,
        title=f"Job for {instance.quote_number}",
        contract_value=instance.grand_total,
        created_by=instance.updated_by,
        updated_by=instance.updated_by,
    )
