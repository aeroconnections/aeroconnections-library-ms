from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("settings/", views.settings, name="settings"),
    path("settings/backups/", views.backup_list, name="backup_list"),
    path("settings/backups/run/", views.backup_run, name="backup_run"),
    path("settings/backups/download/<str:filename>/", views.backup_download, name="backup_download"),
]
