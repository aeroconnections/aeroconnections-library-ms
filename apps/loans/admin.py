from django.contrib import admin

from .models import Loan, ReturnNote


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["book_id_snapshot", "borrower_name", "checkout_date", "due_date", "days_out", "status_display"]
    list_filter = ["status", "checkout_date"]
    search_fields = ["book__book_id", "book__title", "borrower_name"]
    readonly_fields = ["created_at", "updated_at", "days_out", "is_overdue", "is_due_soon"]
    date_hierarchy = "checkout_date"

    def days_out(self, obj):
        return obj.days_out
    days_out.short_description = "Days Out"


@admin.register(ReturnNote)
class ReturnNoteAdmin(admin.ModelAdmin):
    list_display = ["book", "borrower_name", "created_at", "created_by"]
    list_filter = ["created_at"]
    search_fields = ["book__book_id", "book__title", "borrower_name", "note"]
    readonly_fields = ["created_at"]
