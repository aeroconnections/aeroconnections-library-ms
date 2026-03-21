from django.contrib import admin
from .models import Branding


@admin.register(Branding)
class BrandingAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'library_name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['company_name', 'library_name']
    
    fieldsets = (
        ('Company Info', {
            'fields': ('company_name', 'library_name', 'logo')
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color'),
            'description': 'Enter hex color codes (e.g., #DA291C)'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
