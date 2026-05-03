from django.contrib import admin

from .models import Installation, InstallationImage, InstallationTeam


class InstallationImageInline(admin.TabularInline):
    model = InstallationImage
    extra = 0


@admin.register(Installation)
class InstallationAdmin(admin.ModelAdmin):
    list_display = ("job", "scheduled_date", "status", "team")
    list_filter = ("status",)
    inlines = [InstallationImageInline]


@admin.register(InstallationTeam)
class InstallationTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "leader")
