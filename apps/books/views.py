from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.loans.models import ActivityLog, Loan, ReturnNote

from .models import Book, BookCopy


@login_required
def book_list(request):
    books = Book.objects.all()
    search_query = request.GET.get("q")

    if search_query:
        books = books.filter(title__icontains=search_query) | books.filter(
            author__icontains=search_query
        ) | books.filter(book_id__icontains=search_query)

    return render(request, "books/book_list.html", {"books": books})


@login_required
def book_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        isbn = request.POST.get("isbn", "")
        copies = int(request.POST.get("copies", 1))
        book_id = request.POST.get("book_id", "")

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            book_id=book_id if book_id else None,
        )
        book.save()

        for i in range(copies):
            BookCopy.objects.create(book=book)

        ActivityLog.objects.create(
            action=ActivityLog.Action.BOOK_CREATED,
            description=f"Book #{book.book_id} ({book.title}) added with {copies} copy/copies",
            user=request.user,
        )

        messages.success(request, f"Book #{book.book_id} added with {copies} copy/copies.")
        return redirect("books:book_list")

    return render(request, "books/book_create.html")


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copies = book.copies.all()
    loans = Loan.objects.filter(book_copy__in=copies).select_related("book_copy", "created_by").order_by("-checkout_date")
    return_notes = ReturnNote.objects.filter(book_copy__in=copies).select_related("book_copy").order_by("-created_at")
    return render(request, "books/book_detail.html", {
        "book": book,
        "copies": copies,
        "loans": loans,
        "return_notes": return_notes,
    })


@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.isbn = request.POST.get("isbn", "")
        new_copies = int(request.POST.get("copies", book.total_copies))
        new_book_id = request.POST.get("book_id")
        if new_book_id:
            book.book_id = new_book_id
        book.save()

        current_copies = book.total_copies
        if new_copies > current_copies:
            for i in range(new_copies - current_copies):
                BookCopy.objects.create(book=book)
        elif new_copies < current_copies:
            available_copies = book.copies.filter(status=BookCopy.Status.AVAILABLE)
            excess = current_copies - new_copies
            for copy in available_copies[:excess]:
                copy.delete()

        ActivityLog.objects.create(
            action=ActivityLog.Action.BOOK_UPDATED,
            description=f"Book #{book.book_id} ({book.title}) updated",
            user=request.user,
        )

        messages.success(request, f"Book #{book.book_id} updated successfully.")
        return redirect("books:book_detail", pk=book.pk)

    return render(request, "books/book_edit.html", {"book": book})


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    on_loan = book.copies.filter(status=BookCopy.Status.ON_LOAN).exists()
    if on_loan:
        messages.error(request, "Cannot delete a book that has copies currently on loan.")
        return redirect("books:book_list")

    if request.method == "POST":
        book_id = book.book_id
        title = book.title
        book.delete()

        ActivityLog.objects.create(
            action=ActivityLog.Action.BOOK_DELETED,
            description=f"Book #{book_id} ({title}) deleted",
            user=request.user,
        )

        messages.success(request, f"Book #{book_id} deleted successfully.")
        return redirect("books:book_list")

    return render(request, "books/book_confirm_delete.html", {"book": book})


@login_required
def copy_create(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)

    if request.method == "POST":
        BookCopy.objects.create(book=book)
        messages.success(request, f"New copy added to {book.title}.")
        return redirect("books:book_detail", pk=book.pk)

    return redirect("books:book_detail", pk=book.pk)


@login_required
def copy_delete(request, book_pk, copy_pk):
    book = get_object_or_404(Book, pk=book_pk)
    copy = get_object_or_404(BookCopy, pk=copy_pk, book=book)

    if copy.status != BookCopy.Status.AVAILABLE:
        messages.error(request, "Cannot delete a copy that is currently on loan.")
        return redirect("books:book_detail", pk=book.pk)

    if request.method == "POST":
        copy_id = copy.copy_id
        copy.delete()
        messages.success(request, f"Copy {copy_id} deleted.")
        return redirect("books:book_detail", pk=book.pk)

    return redirect("books:book_detail", pk=book.pk)
