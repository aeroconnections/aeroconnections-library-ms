from django.core.validators import RegexValidator
from django.db import models


class LibrarySettings(models.Model):
    LOAN_DURATION_CHOICES = [
        (14, '14 days'),
        (21, '21 days'),
        (30, '30 days'),
        (45, '45 days'),
        (60, '60 days'),
    ]
    DUE_SOON_THRESHOLD_CHOICES = [
        (21, '21 days before due'),
        (25, '25 days before due'),
        (28, '28 days before due'),
    ]

    loan_duration_days = models.PositiveIntegerField(
        default=30,
        choices=LOAN_DURATION_CHOICES,
        help_text="Default loan duration for new loans"
    )
    due_soon_threshold = models.PositiveIntegerField(
        default=25,
        choices=DUE_SOON_THRESHOLD_CHOICES,
        help_text="Days before due date to mark as 'Due Soon'"
    )
    max_books_per_borrower = models.PositiveIntegerField(
        default=5,
        help_text="Maximum books a borrower can have on loan at once"
    )
    notify_on_checkout = models.BooleanField(
        default=False,
        help_text="Send notification when a book is checked out"
    )
    notify_on_return = models.BooleanField(
        default=False,
        help_text="Send notification when a book is returned"
    )
    notify_on_overdue = models.BooleanField(
        default=False,
        help_text="Send notification when a book becomes overdue"
    )
    webhook_url = models.URLField(
        blank=True,
        help_text="Webhook URL to send notifications (e.g., Slack, Discord, custom)"
    )
    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secret key for webhook authentication"
    )
    google_sheets_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Sheets ID for data backup (found in spreadsheet URL)"
    )
    email_notifications_enabled = models.BooleanField(
        default=False,
        help_text="Enable email notifications"
    )
    email_host = models.CharField(
        max_length=255,
        blank=True,
        help_text="SMTP server hostname"
    )
    email_port = models.PositiveIntegerField(
        default=587,
        blank=True,
        help_text="SMTP server port"
    )
    email_username = models.EmailField(
        blank=True,
        help_text="SMTP username"
    )
    email_password = models.CharField(
        max_length=255,
        blank=True,
        help_text="SMTP password (will be encrypted in production)"
    )
    email_from_address = models.EmailField(
        blank=True,
        help_text="From address for outgoing emails"
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Use TLS encryption for email"
    )
    overdue_reminder_days = models.PositiveIntegerField(
        default=7,
        help_text="Days after due date to send overdue reminder"
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Library Settings"
        verbose_name_plural = "Library Settings"

    def save(self, *args, **kwargs):
        if self.is_active:
            LibrarySettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()

    def __str__(self):
        return f"Library Settings (Loan: {self.loan_duration_days} days)"


class Branding(models.Model):
    company_name = models.CharField(max_length=100, default="AeroConnections", blank=True)
    library_name = models.CharField(max_length=100, default="Library Management System")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    show_company_name = models.BooleanField(default=True, help_text="Show company name below logo")
    show_library_name = models.BooleanField(default=True, help_text="Show library name below logo")
    logo_invert = models.BooleanField(default=True, help_text="Invert logo colors (for dark backgrounds)")
    primary_color = models.CharField(
        max_length=7,
        default="#DA291C",
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'Enter a valid hex color code.')]
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#5B6770",
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'Enter a valid hex color code.')]
    )
    accent_color = models.CharField(
        max_length=7,
        default="#C8C9C7",
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$', 'Enter a valid hex color code.')]
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Branding"
        verbose_name_plural = "Branding Settings"

    def save(self, *args, **kwargs):
        if self.is_active:
            Branding.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()

    def __str__(self):
        return f"{self.company_name} - {self.library_name}"
