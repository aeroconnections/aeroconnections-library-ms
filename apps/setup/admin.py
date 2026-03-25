from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import identify_hasher, make_password

from .models import SetupConfig


class SetupConfigAdminForm(forms.ModelForm):
    setup_pin = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="PIN is hidden. Enter a new value to change, or leave blank to keep current.",
    )

    class Meta:
        model = SetupConfig
        fields = "__all__"

    def clean_setup_pin(self):
        value = self.cleaned_data.get("setup_pin")
        if value:
            try:
                identify_hasher(value)
                return value
            except Exception:
                return make_password(value)
        if self.instance and self.instance.pk:
            return self.instance.setup_pin
        return ""


@admin.register(SetupConfig)
class SetupConfigAdmin(admin.ModelAdmin):
    form = SetupConfigAdminForm
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
