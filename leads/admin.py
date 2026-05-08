from django.contrib import admin

from .models import Lead, LeadActivity, LeadAttachment


class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    fields = ("activity_type", "description", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at")


class LeadAttachmentInline(admin.TabularInline):
    model = LeadAttachment
    extra = 0
    fields = ("file", "kind", "caption", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "source", "status", "assigned_to", "created_at")
    list_filter = ("status", "source", "product_interest")
    search_fields = ("full_name", "phone", "email", "company")
    inlines = [LeadAttachmentInline, LeadActivityInline]


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ("lead", "activity_type", "created_at")
    list_filter = ("activity_type",)


@admin.register(LeadAttachment)
class LeadAttachmentAdmin(admin.ModelAdmin):
    list_display = ("lead", "kind", "caption", "created_by", "created_at")
    list_filter = ("kind",)
