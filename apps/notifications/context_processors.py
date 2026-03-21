from django.template import Context, RequestContext


def branding_context(request):
    from apps.notifications.models import Branding
    branding = Branding.get_active()
    
    if branding:
        return {
            'branding': {
                'company_name': branding.company_name,
                'library_name': branding.library_name,
                'logo_url': branding.logo.url if branding.logo else '/static/logo.png',
                'primary_color': branding.primary_color,
                'secondary_color': branding.secondary_color,
                'accent_color': branding.accent_color,
            }
        }
    
    from django.conf import settings
    return {
        'branding': {
            'company_name': getattr(settings, 'COMPANY_NAME', 'AeroConnections'),
            'library_name': getattr(settings, 'LIBRARY_NAME', 'Library Management System'),
            'logo_url': getattr(settings, 'LOGO_URL', '/static/logo.png'),
            'primary_color': getattr(settings, 'PRIMARY_COLOR', '#DA291C'),
            'secondary_color': getattr(settings, 'SECONDARY_COLOR', '#5B6770'),
            'accent_color': getattr(settings, 'ACCENT_COLOR', '#C8C9C7'),
        }
    }
