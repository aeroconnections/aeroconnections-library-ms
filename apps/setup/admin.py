from django.contrib import admin

from .models import SetupConfig


@admin.register(SetupConfig)
class SetupConfigAdmin(admin.ModelAdmin):
    list_display = ["setup_completed", "domain", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Setup Status", {
            "fields": ("setup_completed",)
        }),
        ("Security", {
            "fields": ("setup_pin", "domain")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
