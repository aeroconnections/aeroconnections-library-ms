from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["book_id", "title", "author", "status", "current_borrower", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["book_id", "title", "author", "isbn"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["book_id"]

    def current_borrower(self, obj):
        return obj.current_borrower or "-"
    current_borrower.short_description = "Borrower"
