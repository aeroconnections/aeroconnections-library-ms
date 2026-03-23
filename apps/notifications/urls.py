from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("settings/sheets/", views.sheets_setup, name="sheets_setup"),
    path("settings/sheets/auth/", views.sheets_auth, name="sheets_auth"),
    path("settings/sheets/callback/", views.sheets_callback, name="sheets_callback"),
    path("settings/sheets/auth-console/", views.sheets_auth_console, name="sheets_auth_console"),
    path("settings/sheets/callback-console/", views.sheets_callback_console, name="sheets_callback_console"),
    path("settings/sheets/sync/", views.sheets_sync, name="sheets_sync"),
    path("settings/sheets/disconnect/", views.sheets_disconnect, name="sheets_disconnect"),
]
