from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SetupConfig(models.Model):
    setup_completed = models.BooleanField(default=False)
    setup_pin = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Setup Configuration"
        verbose_name_plural = "Setup Configuration"

    def __str__(self):
        return f"Setup Config (Completed: {self.setup_completed})"

    @classmethod
    def is_configured(cls):
        return cls.objects.exists() and cls.objects.first().setup_completed

    @classmethod
    def get_config(cls):
        return cls.objects.first() or cls.objects.create()

    @classmethod
    def has_users(cls):
        return User.objects.exists()

    def save(self, *args, **kwargs):
        if not SetupConfig.objects.exists():
            super().save(*args, **kwargs)
        else:
            self.pk = SetupConfig.objects.first().pk
            super().save(*args, **kwargs)
