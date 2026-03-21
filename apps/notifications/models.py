from django.core.validators import RegexValidator
from django.db import models


class Branding(models.Model):
    company_name = models.CharField(max_length=100, default="AeroConnections", blank=True)
    library_name = models.CharField(max_length=100, default="Library Management System")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    show_company_name = models.BooleanField(default=True, help_text="Show company name next to logo")
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
