from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.books.models import Book

from .models import Loan, ReturnNote


@login_required
def loan_list(request):
    loans = Loan.objects.select_related("book").all()
    status_filter = request.GET.get("status")
    if status_filter:
        loans = loans.filter(status=status_filter)

    stats = {
        "total": Loan.objects.count(),
        "active": Loan.objects.filter(status__in=["active", "overdue"]).count(),
        "due_soon": Loan.objects.filter(
            status="active",
            checkout_date__lte=timezone.now().date() - timedelta(days=25)
        ).exclude(
            checkout_date__lte=timezone.now().date() - timedelta(days=30)
        ).count(),
        "overdue": Loan.objects.filter(
            checkout_date__lt=timezone.now().date() - timedelta(days=30)
        ).exclude(status="returned").count(),
    }

    return render(request, "loans/loan_list.html", {
        "loans": loans,
        "stats": stats
    })


@login_required
def loan_create(request):
    if request.method == "POST":
        book_id = request.POST.get("book")
        borrower_name = request.POST.get("borrower_name")

        book = get_object_or_404(Book, id=book_id)

        if book.status == Book.Status.ON_LOAN:
            messages.error(request, "This book is already on loan.")
            return redirect("loans:loan_create")

        checkout_date = timezone.now().date()
        due_date = checkout_date + timedelta(days=Loan.LOAN_DURATION_DAYS)

        Loan.objects.create(
            book=book,
            book_id_snapshot=book.book_id,
            borrower_name=borrower_name,
            checkout_date=checkout_date,
            due_date=due_date,
            created_by=request.user,
        )

        book.status = Book.Status.ON_LOAN
        book.save()

        messages.success(request, f"Book #{book.book_id} checked out to {borrower_name}.")
        return redirect("loans:loan_list")

    books = Book.objects.filter(status=Book.Status.AVAILABLE)
    return render(request, "loans/loan_create.html", {"books": books})


@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    return render(request, "loans/loan_detail.html", {"loan": loan})


@login_required
def loan_return(request, pk):
    loan = get_object_or_404(Loan, pk=pk)

    if loan.status == Loan.Status.RETURNED:
        messages.error(request, "This loan has already been returned.")
        return redirect("loans:loan_list")

    if request.method == "POST":
        return_date = timezone.now().date()
        notes = request.POST.get("notes", "")
        image = request.FILES.get("damage_image")

        loan.return_date = return_date
        loan.status = Loan.Status.RETURNED
        loan.notes = notes
        loan.damage_image = image
        loan.save()

        ReturnNote.objects.create(
            loan=loan,
            book=loan.book,
            borrower_name=loan.borrower_name,
            note=notes,
            image=image,
            created_by=request.user,
        )

        loan.book.status = Book.Status.AVAILABLE
        loan.book.save()

        messages.success(request, f"Book #{loan.book.book_id} returned successfully.")
        return redirect("loans:loan_list")

    return render(request, "loans/loan_return.html", {"loan": loan})


@login_required
def return_notes(request):
    notes = ReturnNote.objects.select_related("book", "loan").all()

    book_filter = request.GET.get("book")
    if book_filter:
        notes = notes.filter(book__book_id=book_filter)

    return render(request, "loans/return_notes.html", {"notes": notes})


@login_required
def dashboard(request):
    books_count = Book.objects.count()
    active_loans = Loan.objects.filter(status__in=["active", "overdue"]).count()
    overdue_loans = Loan.objects.filter(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    ).exclude(status="returned").count()
    due_soon_loans = Loan.objects.filter(
        status="active",
        checkout_date__lte=timezone.now().date() - timedelta(days=25)
    ).exclude(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    )

    recent_loans = Loan.objects.select_related("book").order_by("-created_at")[:5]
    overdue_list = Loan.objects.filter(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    ).exclude(status="returned").select_related("book")[:10]

    stats = {
        "books": books_count,
        "active": active_loans,
        "overdue": overdue_loans,
        "due_soon": due_soon_loans.count(),
    }

    return render(request, "loans/dashboard.html", {
        "stats": stats,
        "recent_loans": recent_loans,
        "overdue_loans": overdue_list,
        "due_soon_loans": due_soon_loans,
    })
