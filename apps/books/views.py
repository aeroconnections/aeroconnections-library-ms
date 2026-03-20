from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Book


@login_required
def book_list(request):
    books = Book.objects.all()
    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")
    
    if status_filter:
        if status_filter == "available":
            books = books.filter(status=Book.Status.AVAILABLE)
        elif status_filter == "on_loan":
            books = books.filter(status=Book.Status.ON_LOAN)
    
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
        book_id = request.POST.get("book_id", "")
        
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            book_id=book_id if book_id else None,
        )
        book.save()
        
        messages.success(request, f"Book #{book.book_id} added successfully.")
        return redirect("books:book_list")
    
    return render(request, "books/book_create.html")


@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "books/book_detail.html", {"book": book})


@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.isbn = request.POST.get("isbn", "")
        new_book_id = request.POST.get("book_id")
        if new_book_id:
            book.book_id = new_book_id
        book.save()
        
        messages.success(request, f"Book #{book.book_id} updated successfully.")
        return redirect("books:book_detail", pk=book.pk)
    
    return render(request, "books/book_edit.html", {"book": book})


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if book.status == Book.Status.ON_LOAN:
        messages.error(request, "Cannot delete a book that is currently on loan.")
        return redirect("books:book_list")
    
    if request.method == "POST":
        book_id = book.book_id
        book.delete()
        messages.success(request, f"Book #{book_id} deleted successfully.")
        return redirect("books:book_list")
    
    return render(request, "books/book_confirm_delete.html", {"book": book})
