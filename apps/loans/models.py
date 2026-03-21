from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.books.models import Book


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"

    LOAN_DURATION_DAYS = 30
    DUE_SOON_THRESHOLD = 25

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    book_id_snapshot = models.CharField(max_length=10, help_text="Snapshot of book's ID at checkout")
    borrower_name = models.CharField(max_length=255)
    checkout_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    notes = models.TextField(blank=True, help_text="Return notes")
    damage_image = models.ImageField(
        upload_to="returns/",
        null=True,
        blank=True,
        help_text="Optional damage photo"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loans_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-checkout_date"]

    def __str__(self):
        return f"#{self.book_id_snapshot} - {self.borrower_name}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=self.LOAN_DURATION_DAYS)
        if not self.book_id_snapshot:
            self.book_id_snapshot = self.book.book_id
        super().save(*args, **kwargs)

    @property
    def days_out(self):
        if self.return_date:
            return (self.return_date - self.checkout_date).days
        return (timezone.now().date() - self.checkout_date).days

    @property
    def days_until_due(self):
        return (self.due_date - timezone.now().date()).days

    @property
    def is_due_soon(self):
        if self.status == self.Status.RETURNED:
            return False
        return self.days_out >= self.DUE_SOON_THRESHOLD and self.days_out < self.LOAN_DURATION_DAYS

    @property
    def is_overdue(self):
        if self.status == self.Status.RETURNED:
            return False
        return self.days_out > self.LOAN_DURATION_DAYS

    @property
    def status_display(self):
        if self.status == self.Status.RETURNED:
            return "Returned"
        if self.is_overdue:
            return "Overdue"
        if self.is_due_soon:
            return "Due Soon"
        return "Active"

    @property
    def status_color(self):
        if self.status == self.Status.RETURNED:
            return "success"
        if self.is_overdue:
            return "danger"
        if self.is_due_soon:
            return "warning"
        return "on_loan"


class ReturnNote(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="return_notes"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="return_notes"
    )
    borrower_name = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="returns/",
        null=True,
        blank=True,
        help_text="Optional damage photo"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="return_notes_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Return Note"
        verbose_name_plural = "Return Notes"

    def __str__(self):
        return f"Return Note for #{self.book.book_id} - {self.borrower_name}"
