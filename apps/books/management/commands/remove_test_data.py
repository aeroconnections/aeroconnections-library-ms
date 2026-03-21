from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.books.models import Book, BookCopy
from apps.borrowers.models import Borrower
from apps.loans.models import ActivityLog, Loan, ReturnNote

User = get_user_model()


class Command(BaseCommand):
    help = "Remove all test data from the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-users",
            action="store_true",
            help="Keep test users (admin, staff)",
        )
        parser.add_argument(
            "--keep-books",
            action="store_true",
            help="Keep books and copies",
        )

    def handle(self, *args, **options):
        confirm = input(
            "This will delete all loans, return notes, borrowers, and optionally users and books. "
            "Are you sure? [y/N] "
        )
        if confirm.lower() != 'y':
            self.stdout.write(self.style.WARNING("Cancelled."))
            return

        deleted_loans = Loan.objects.count()
        deleted_notes = ReturnNote.objects.count()
        deleted_logs = ActivityLog.objects.count()
        deleted_borrowers = Borrower.objects.count()
        deleted_copies = BookCopy.objects.count()
        deleted_books = Book.objects.count()
        deleted_users = 0

        ReturnNote.objects.all().delete()
        Loan.objects.all().delete()
        ActivityLog.objects.all().delete()
        self.stdout.write(f"  Deleted {deleted_loans} loans")
        self.stdout.write(f"  Deleted {deleted_notes} return notes")
        self.stdout.write(f"  Deleted {deleted_logs} activity logs")

        if not options["keep_users"]:
            deleted_users = User.objects.filter(username__in=["admin", "staff"]).delete()[0]
            self.stdout.write(f"  Deleted {deleted_users} users")

        if not options["keep_books"]:
            BookCopy.objects.all().delete()
            Book.objects.all().delete()
            self.stdout.write(f"  Deleted {deleted_copies} book copies")
            self.stdout.write(f"  Deleted {deleted_books} books")

        if not options["keep_users"]:
            Borrower.objects.all().delete()
            self.stdout.write(f"  Deleted {deleted_borrowers} borrowers")

        self.stdout.write(self.style.SUCCESS("\nTest data removed successfully!"))
