from django.contrib import admin

from .models import Job, JobMaterial, JobStatusUpdate


class JobMaterialInline(admin.TabularInline):
    model = JobMaterial
    extra = 0


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("job_number", "title", "customer", "status", "contract_value", "start_date")
    list_filter = ("status",)
    inlines = [JobMaterialInline]
    search_fields = ("job_number", "title", "customer__full_name")


@admin.register(JobStatusUpdate)
class JobStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ("job", "from_status", "to_status", "created_at", "created_by")
