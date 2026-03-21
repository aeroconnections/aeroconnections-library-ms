from datetime import timedelta
from random import choice

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.books.models import Book, BookCopy
from apps.borrowers.models import Borrower
from apps.loans.models import ActivityLog, Loan, ReturnNote

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with sample test data"

    def handle(self, *args, **options):
        self.stdout.write("Creating test data...")

        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@example.com",
            },
        )
        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin/admin123)"))

        staff, created = User.objects.get_or_create(
            username="staff",
            defaults={
                "is_staff": True,
                "is_superuser": False,
                "email": "staff@example.com",
            },
        )
        if created:
            staff.set_password("staff123")
            staff.save()
            self.stdout.write(self.style.SUCCESS("Created staff user (staff/staff123)"))

        books_data = [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0743273565", "copies": 2},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0061120084", "copies": 1},
            {"title": "1984", "author": "George Orwell", "isbn": "978-0451524935", "copies": 2},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "978-0141439518", "copies": 1},
            {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "978-0316769488", "copies": 1},
            {"title": "Brave New World", "author": "Aldous Huxley", "isbn": "978-0060850524", "copies": 1},
            {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "978-0618640157", "copies": 1},
            {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "isbn": "978-0590353427", "copies": 2},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "978-0547928227", "copies": 1},
            {"title": "Fahrenheit 451", "author": "Ray Bradbury", "isbn": "978-1451673319", "copies": 1},
            {"title": "Animal Farm", "author": "George Orwell", "isbn": "978-0451526342", "copies": 1},
            {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "isbn": "978-0141439570", "copies": 1},
        ]

        books = []
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                title=book_data["title"],
                defaults={
                    "author": book_data["author"],
                    "isbn": book_data["isbn"],
                },
            )
            books.append(book)
            if created:
                for i in range(book_data["copies"]):
                    BookCopy.objects.create(book=book)
                self.stdout.write(f"  Created book: {book.title} ({book_data['copies']} copies)")

        borrowers_data = [
            {"full_name": "John Smith", "email": "john.smith@example.com", "phone": "555-0101", "employment_type": "permanent"},
            {"full_name": "Sarah Johnson", "email": "sarah.johnson@example.com", "phone": "555-0102", "employment_type": "permanent"},
            {"full_name": "Michael Brown", "email": "michael.brown@example.com", "phone": "555-0103", "employment_type": "intern"},
            {"full_name": "Emily Davis", "email": "emily.davis@example.com", "phone": "555-0104", "employment_type": "permanent"},
            {"full_name": "David Wilson", "email": "david.wilson@example.com", "phone": "555-0105", "employment_type": "temporary"},
            {"full_name": "Jennifer Martinez", "email": "jennifer.martinez@example.com", "phone": "555-0106", "employment_type": "permanent"},
            {"full_name": "Robert Anderson", "email": "robert.anderson@example.com", "phone": "555-0107", "employment_type": "permanent"},
            {"full_name": "Lisa Taylor", "email": "lisa.taylor@example.com", "phone": "555-0108", "employment_type": "intern"},
            {"full_name": "James Thomas", "email": "james.thomas@example.com", "phone": "555-0109", "employment_type": "permanent"},
            {"full_name": "Maria Garcia", "email": "maria.garcia@example.com", "phone": "555-0110", "employment_type": "permanent"},
        ]

        borrowers = []
        for borrower_data in borrowers_data:
            borrower, created = Borrower.objects.get_or_create(
                email=borrower_data["email"],
                defaults=borrower_data,
            )
            borrowers.append(borrower)
            if created:
                self.stdout.write(f"  Created borrower: {borrower.full_name}")

        now = timezone.now()

        available_copies = list(BookCopy.objects.filter(status=BookCopy.Status.AVAILABLE))

        loan_scenarios = [
            {"days_ago": 5},
            {"days_ago": 15},
            {"days_ago": 25},
            {"days_ago": 32},
            {"days_ago": 45},
            {"days_ago": 10, "returned": True},
            {"days_ago": 20, "returned": True},
            {"days_ago": 7},
            {"days_ago": 28},
            {"days_ago": 35},
        ]

        for i, scenario in enumerate(loan_scenarios):
            if not available_copies:
                break

            copy = available_copies.pop(0)
            borrower = borrowers[i % len(borrowers)]
            checkout_date = now - timedelta(days=scenario["days_ago"])
            is_returned = scenario.get("returned", False)

            copy.status = BookCopy.Status.ON_LOAN if not is_returned else BookCopy.Status.AVAILABLE
            copy.save()

            loan = Loan.objects.create(
                book_copy=copy,
                copy_id_snapshot=copy.copy_id,
                book_title_snapshot=copy.book.title,
                borrower_name=borrower.full_name,
                checkout_date=checkout_date,
                status=Loan.Status.RETURNED if is_returned else Loan.Status.ACTIVE,
                return_date=now if is_returned else None,
            )
            self.stdout.write(f"  Created loan: {copy.copy_id} -> {borrower.full_name}")

            if is_returned:
                copy.status = BookCopy.Status.AVAILABLE
                copy.save()

                notes_list = [
                    "Book returned in good condition.",
                    "Minor wear on cover, otherwise fine.",
                    "Returned on time, no issues.",
                ]
                ReturnNote.objects.create(
                    loan=loan,
                    book_copy=copy,
                    borrower_name=borrower.full_name,
                    note=choice(notes_list),
                    created_by=staff,
                )

                ActivityLog.objects.create(
                    action=ActivityLog.Action.RETURN,
                    description=f"Copy {copy.copy_id} ({copy.book.title}) returned by {borrower.full_name}",
                    user=staff,
                )
            else:
                ActivityLog.objects.create(
                    action=ActivityLog.Action.CHECKOUT,
                    description=f"Copy {copy.copy_id} ({copy.book.title}) checked out to {borrower.full_name}",
                    user=staff,
                )

        self.stdout.write(self.style.SUCCESS("\nTest data created successfully!"))
        self.stdout.write("\nUsers created:")
        self.stdout.write("  - admin / admin123 (superuser)")
        self.stdout.write("  - staff / staff123 (staff)")
        self.stdout.write(f"\nBorrowers: {len(borrowers)}")
        self.stdout.write(f"Books: {len(books)}")
        self.stdout.write(f"Copies: {BookCopy.objects.count()}")
