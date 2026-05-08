from django.contrib import admin

from .models import Job, JobStatusUpdate, JobVariation


class JobVariationInline(admin.TabularInline):
    model = JobVariation
    extra = 0


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "job_number",
        "title",
        "customer",
        "status",
        "contract_value",
        "start_date",
    )
    list_filter = ("status",)
    inlines = [JobVariationInline]
    search_fields = ("job_number", "title", "customer__full_name")


@admin.register(JobVariation)
class JobVariationAdmin(admin.ModelAdmin):
    list_display = ("job", "amount", "reason", "approved_at", "approved_by")
    list_filter = ("reason",)


@admin.register(JobStatusUpdate)
class JobStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ("job", "from_status", "to_status", "created_at", "created_by")
