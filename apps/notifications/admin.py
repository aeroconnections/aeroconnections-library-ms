from django import forms
from django.contrib import admin

from .models import Branding, LibrarySettings


class LibrarySettingsAdminForm(forms.ModelForm):
    webhook_secret = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep current value.",
    )
    smb_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep current value.",
    )
    email_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep current value.",
    )

    class Meta:
        model = LibrarySettings
        fields = "__all__"

    def clean_webhook_secret(self):
        value = self.cleaned_data.get("webhook_secret")
        if value:
            return value
        if self.instance and self.instance.pk:
            return self.instance.webhook_secret
        return ""

    def clean_smb_password(self):
        value = self.cleaned_data.get("smb_password")
        if value:
            return value
        if self.instance and self.instance.pk:
            return self.instance.smb_password
        return ""

    def clean_email_password(self):
        value = self.cleaned_data.get("email_password")
        if value:
            return value
        if self.instance and self.instance.pk:
            return self.instance.email_password
        return ""


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    form = LibrarySettingsAdminForm
    list_display = ['__str__', 'loan_duration_days', 'due_soon_threshold', 'backup_enabled', 'is_active', 'updated_at']
    list_filter = ['is_active', 'backup_enabled']

    fieldsets = (
        ('Loan Settings', {
            'fields': ('loan_duration_days', 'due_soon_threshold', 'max_books_per_borrower')
        }),
        ('Notifications', {
            'fields': ('notify_on_checkout', 'notify_on_return', 'notify_on_overdue', 'overdue_reminder_days')
        }),
        ('Notification Webhook', {
            'fields': ('webhook_url', 'webhook_secret'),
            'description': 'Configure webhook URL for external notifications (Slack, Discord, custom). '
                          'Leave blank to keep current value.'
        }),
        ('Backup Settings', {
            'fields': ('backup_enabled', 'backup_hour', 'backup_retention_days', 'backup_mount_type', 'backup_mount_path', 'backup_mount_options'),
            'classes': ('collapse',),
        }),
        ('SMB Settings', {
            'fields': ('smb_server', 'smb_username', 'smb_password', 'smb_domain'),
            'description': 'Password is hidden. Enter a new value to change, or leave blank to keep current.',
            'classes': ('collapse',),
        }),
        ('System Alerts', {
            'fields': ('system_alert_enabled', 'system_alert_webhook_url'),
            'description': 'System alerts for backup status and errors (separate from notification webhook)'
        }),
        ('Email Settings', {
            'fields': ('email_notifications_enabled', 'email_host', 'email_port', 'email_username', 'email_password', 'email_from_address', 'email_use_tls'),
            'description': 'Password is hidden. Enter a new value to change, or leave blank to keep current.',
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Branding)
class BrandingAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'library_name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['company_name', 'library_name']

    fieldsets = (
        ('Logo', {
            'fields': ('logo', 'logo_invert')
        }),
        ('Names', {
            'fields': ('company_name', 'show_company_name', 'library_name', 'show_library_name')
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color'),
            'description': 'Enter hex color codes (e.g., #DA291C)'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
