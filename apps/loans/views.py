from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.books.models import Book, BookCopy
from apps.borrowers.models import Borrower

from .models import ActivityLog, Loan, ReturnNote


def log_activity(action, description, user):
    ActivityLog.objects.create(
        action=action,
        description=description,
        user=user
    )


@login_required
def loan_list(request):
    active_loans = Loan.objects.select_related("book_copy", "book_copy__book").filter(
        status__in=["active", "overdue"]
    ).order_by("-checkout_date")
    returned_loans = Loan.objects.select_related("book_copy", "book_copy__book").filter(
        status="returned"
    ).order_by("-return_date")

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
        "active_loans": active_loans,
        "returned_loans": returned_loans,
        "stats": stats
    })


@login_required
def loan_create(request):
    if request.method == "POST":
        copy_id = request.POST.get("copy")
        borrower_id = request.POST.get("borrower")

        book_copy = get_object_or_404(BookCopy, id=copy_id)
        borrower = get_object_or_404(Borrower, id=borrower_id)

        if not borrower.is_active:
            messages.error(request, "This borrower is no longer active.")
            return redirect("loans:loan_create")

        if not book_copy.is_available:
            messages.error(request, f"Copy {book_copy.copy_id} is not available.")
            return redirect("loans:loan_create")

        checkout_date = timezone.now().date()
        due_date = checkout_date + timedelta(days=Loan.LOAN_DURATION_DAYS)

        Loan.objects.create(
            book_copy=book_copy,
            copy_id_snapshot=book_copy.copy_id,
            book_title_snapshot=book_copy.book.title,
            borrower_name=borrower.full_name,
            checkout_date=checkout_date,
            due_date=due_date,
            created_by=request.user,
        )

        book_copy.status = BookCopy.Status.ON_LOAN
        book_copy.save()

        log_activity(
            ActivityLog.Action.CHECKOUT,
            f"Copy {book_copy.copy_id} ({book_copy.book.title}) checked out to {borrower.full_name}",
            request.user
        )

        messages.success(request, f"Copy {book_copy.copy_id} checked out to {borrower.full_name}.")
        return redirect("loans:loan_list")

    borrowers = Borrower.objects.filter(is_active=True)
    available_copies = BookCopy.objects.filter(status=BookCopy.Status.AVAILABLE).select_related("book")
    return render(request, "loans/loan_create.html", {"copies": available_copies, "borrowers": borrowers})


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

        if notes or image:
            ReturnNote.objects.create(
                loan=loan,
                book_copy=loan.book_copy,
                borrower_name=loan.borrower_name,
                note=notes,
                image=image,
                created_by=request.user,
            )

        loan.book_copy.status = BookCopy.Status.AVAILABLE
        loan.book_copy.save()

        log_activity(
            ActivityLog.Action.RETURN,
            f"Copy {loan.book_copy.copy_id} ({loan.book_copy.book.title}) returned by {loan.borrower_name}",
            request.user
        )

        messages.success(request, f"Copy {loan.book_copy.copy_id} returned successfully.")
        return redirect("loans:loan_list")

    return render(request, "loans/loan_return.html", {"loan": loan})


@login_required
def return_notes(request):
    notes = ReturnNote.objects.select_related("book_copy", "book_copy__book", "loan").all()

    book_filter = request.GET.get("book")
    if book_filter:
        notes = notes.filter(book_copy__copy_id__icontains=book_filter)

    return render(request, "loans/return_notes.html", {"notes": notes})


@login_required
def activity_log(request):
    logs = ActivityLog.objects.select_related("user").all()

    action_filter = request.GET.get("action")
    if action_filter:
        logs = logs.filter(action=action_filter)

    return render(request, "loans/activity_log.html", {"logs": logs})


@login_required
def dashboard(request):
    books_count = Book.objects.count()
    copies_count = BookCopy.objects.count()
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

    recent_loans = Loan.objects.select_related("book_copy", "book_copy__book").order_by("-created_at")[:5]
    overdue_list = Loan.objects.filter(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    ).exclude(status="returned").select_related("book_copy", "book_copy__book")[:10]

    stats = {
        "books": books_count,
        "copies": copies_count,
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
