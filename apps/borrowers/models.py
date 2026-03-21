from django.db import models


class Borrower(models.Model):
    class EmploymentType(models.TextChoices):
        PERMANENT = "permanent", "Permanent Employee"
        INTERN = "intern", "Intern"
        TEMPORARY = "temporary", "Temporary Employee"

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.PERMANENT,
    )
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_contact = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    @property
    def needs_guardian(self):
        return self.employment_type in [self.EmploymentType.INTERN, self.EmploymentType.TEMPORARY]
