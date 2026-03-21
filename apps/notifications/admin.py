from django.contrib import admin

from .models import Branding, LibrarySettings


@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'loan_duration_days', 'due_soon_threshold', 'is_active', 'updated_at']
    list_filter = ['is_active']

    fieldsets = (
        ('Loan Settings', {
            'fields': ('loan_duration_days', 'due_soon_threshold', 'max_books_per_borrower')
        }),
        ('Notifications', {
            'fields': ('notify_on_checkout', 'notify_on_return', 'notify_on_overdue', 'overdue_reminder_days')
        }),
        ('Webhook', {
            'fields': ('webhook_url', 'webhook_secret'),
            'description': 'Configure webhook URL for external notifications (Slack, Discord, custom)'
        }),
        ('Google Sheets Backup', {
            'fields': ('google_sheets_id',),
            'description': 'Enter Google Sheets ID from the spreadsheet URL for data backup'
        }),
        ('Email Settings', {
            'fields': ('email_notifications_enabled', 'email_host', 'email_port', 'email_username', 'email_password', 'email_from_address', 'email_use_tls'),
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
