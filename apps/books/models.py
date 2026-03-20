from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        ON_LOAN = "on_loan", "On Loan"

    book_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        help_text="Auto-generated internal ID. Can be edited."
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["book_id"]

    def __str__(self):
        return f"#{self.book_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.book_id:
            last_book = Book.objects.order_by("-book_id").first()
            if last_book and last_book.book_id:
                try:
                    last_num = int(last_book.book_id)
                    self.book_id = str(last_num + 1).zfill(2)
                except ValueError:
                    self.book_id = "01"
            else:
                self.book_id = "01"
        super().save(*args, **kwargs)

    @property
    def current_loan(self):
        return self.loans.filter(status__in=["active", "overdue"]).first()

    @property
    def is_on_loan(self):
        return self.loans.filter(status__in=["active", "overdue"]).exists()

    @property
    def days_out(self):
        loan = self.current_loan
        if loan:
            return loan.days_out
        return 0

    @property
    def current_borrower(self):
        loan = self.current_loan
        return loan.borrower_name if loan else None
