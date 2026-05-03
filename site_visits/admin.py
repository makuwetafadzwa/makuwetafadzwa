from django.contrib import admin

from .models import Measurement, SiteVisit, SiteVisitImage


class MeasurementInline(admin.TabularInline):
    model = Measurement
    extra = 0


class SiteVisitImageInline(admin.TabularInline):
    model = SiteVisitImage
    extra = 0


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ("customer", "scheduled_date", "status", "assigned_to")
    list_filter = ("status",)
    inlines = [MeasurementInline, SiteVisitImageInline]


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("site_visit", "location_label", "product_type", "width_mm", "height_mm")
