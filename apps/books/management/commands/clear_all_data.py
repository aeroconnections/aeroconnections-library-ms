from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.books.models import Book, BookCopy
from apps.borrowers.models import Borrower
from apps.loans.models import ActivityLog, Loan, ReturnNote
from apps.notifications.models import Branding, LibrarySettings
from apps.setup.models import SetupConfig

User = get_user_model()


class Command(BaseCommand):
    help = "Clear all data from the database (requires superuser)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args, **options):
        if not options["noinput"]:
            confirm = input(
                "WARNING: This will delete ALL data including admin users, books, borrowers, loans, and settings.\n"
                "Type 'yes' to confirm: "
            )
            if confirm.lower() != "yes":
                self.stdout.write(self.style.WARNING("Cancelled."))
                return

        deleted_counts = {}

        deleted_counts["book copies"] = BookCopy.objects.count()
        deleted_counts["books"] = Book.objects.count()
        BookCopy.objects.all().delete()
        Book.objects.all().delete()

        deleted_counts["loans"] = Loan.objects.count()
        deleted_counts["return notes"] = ReturnNote.objects.count()
        deleted_counts["activity logs"] = ActivityLog.objects.count()
        ReturnNote.objects.all().delete()
        Loan.objects.all().delete()
        ActivityLog.objects.all().delete()

        deleted_counts["borrowers"] = Borrower.objects.count()
        Borrower.objects.all().delete()

        deleted_counts["users"] = User.objects.count()
        User.objects.all().delete()

        LibrarySettings.objects.all().delete()
        Branding.objects.all().delete()
        SetupConfig.objects.all().delete()

        self.stdout.write("\nDeleted:")
        for item, count in deleted_counts.items():
            self.stdout.write(f"  - {count} {item}")

        self.stdout.write(self.style.SUCCESS("\nAll data cleared successfully!"))
        self.stdout.write("Run the setup wizard at /setup/ to reconfigure.")
