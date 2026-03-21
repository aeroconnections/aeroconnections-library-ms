from django.contrib import admin

from .models import Book, BookCopy


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["book_id", "title", "author", "total_copies", "available_copies", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["book_id", "title", "author", "isbn"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["book_id"]


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ["copy_id", "book", "status", "condition", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["copy_id", "book__book_id", "book__title"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["copy_id"]
