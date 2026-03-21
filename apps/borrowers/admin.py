from django.contrib import admin

from .models import Borrower


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "employment_type", "is_active", "created_at"]
    list_filter = ["employment_type", "is_active"]
    search_fields = ["full_name", "email", "phone"]
    ordering = ["full_name"]
