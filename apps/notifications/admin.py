from django.contrib import admin

from .models import Branding, LibrarySettings


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
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
            'fields': ('webhook_url', 'webhook_secret_display', 'webhook_secret'),
            'description': 'Configure webhook URL for external notifications (Slack, Discord, custom). '
                          'Leave blank to keep current value.'
        }),
        ('Backup Settings', {
            'fields': ('backup_enabled', 'backup_hour', 'backup_retention_days', 'backup_mount_type', 'backup_mount_path', 'backup_mount_options'),
            'classes': ('collapse',),
        }),
        ('SMB Settings', {
            'fields': ('smb_server', 'smb_username', 'smb_password_display', 'smb_password', 'smb_domain'),
            'description': 'Password is masked. Enter new value to change, or leave blank to keep current.',
            'classes': ('collapse',),
        }),
        ('System Alerts', {
            'fields': ('system_alert_enabled', 'system_alert_webhook_url'),
            'description': 'System alerts for backup status and errors (separate from notification webhook)'
        }),
        ('Email Settings', {
            'fields': ('email_notifications_enabled', 'email_host', 'email_port', 'email_username', 'email_password_display', 'email_password', 'email_from_address', 'email_use_tls'),
            'description': 'Password is masked. Enter new value to change, or leave blank to keep current.',
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ('webhook_secret_display', 'smb_password_display', 'email_password_display')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('webhook_secret', 'smb_password', 'email_password')
        return self.readonly_fields

    def webhook_secret_display(self, obj):
        if obj and obj.webhook_secret:
            return "********"
        return "(not set)"
    webhook_secret_display.short_description = "Webhook Secret"

    def smb_password_display(self, obj):
        if obj and obj.smb_password:
            return "********"
        return "(not set)"
    smb_password_display.short_description = "SMB Password"

    def email_password_display(self, obj):
        if obj and obj.email_password:
            return "********"
        return "(not set)"
    email_password_display.short_description = "Email Password"


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
