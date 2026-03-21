from django.contrib import admin

from .models import ActivityLog, Loan, ReturnNote


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["copy_id_snapshot", "borrower_name", "checkout_date", "due_date", "status_display"]
    list_filter = ["status", "checkout_date"]
    search_fields = ["book_copy__copy_id", "book_title_snapshot", "borrower_name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "checkout_date"


@admin.register(ReturnNote)
class ReturnNoteAdmin(admin.ModelAdmin):
    list_display = ["book_copy", "borrower_name", "created_at", "created_by"]
    list_filter = ["created_at"]
    search_fields = ["book_copy__copy_id", "borrower_name", "note"]
    readonly_fields = ["created_at"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "action", "description", "user"]
    list_filter = ["action", "timestamp"]
    search_fields = ["description", "user__username"]
    readonly_fields = ["timestamp", "action", "description", "user"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
