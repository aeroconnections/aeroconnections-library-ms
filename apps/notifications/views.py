from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render

from .models import LibrarySettings


def is_superadmin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superadmin)
def settings(request):
    settings_obj = LibrarySettings.get_active()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_backup":
            settings_obj.backup_enabled = request.POST.get("backup_enabled") == "on"
            settings_obj.backup_hour = int(request.POST.get("backup_hour", 2))
            settings_obj.backup_retention_days = int(request.POST.get("backup_retention_days", 14))
            settings_obj.backup_mount_type = request.POST.get("backup_mount_type", "local")
            settings_obj.backup_mount_path = request.POST.get("backup_mount_path", "")
            settings_obj.backup_mount_options = request.POST.get("backup_mount_options", "")
            settings_obj.smb_server = request.POST.get("smb_server", "")
            settings_obj.smb_username = request.POST.get("smb_username", "")
            settings_obj.smb_password = request.POST.get("smb_password", "")
            settings_obj.smb_domain = request.POST.get("smb_domain", "")
            settings_obj.save()
            messages.success(request, "Backup settings updated successfully.")
            return redirect("notifications:settings")

        elif action == "update_system_alerts":
            settings_obj.system_alert_enabled = request.POST.get("system_alert_enabled") == "on"
            settings_obj.system_alert_webhook_url = request.POST.get("system_alert_webhook_url", "")
            settings_obj.save()
            messages.success(request, "System alert settings updated.")
            return redirect("notifications:settings")

    hours = list(range(24))
    return render(request, "notifications/settings.html", {
        "settings_obj": settings_obj,
        "hours": hours,
    })


@login_required
@user_passes_test(is_superadmin)
def backup_list(request):
    from .services.backup import BackupService

    backup_service = BackupService()
    backups = backup_service.list_backups()
    last_backup = backup_service.get_last_backup_info()

    return render(request, "notifications/backup_list.html", {
        "backups": backups,
        "last_backup": last_backup,
    })


@login_required
@user_passes_test(is_superadmin)
def backup_run(request):
    from .services import SystemAlertService
    from .services.backup import BackupService

    if request.method == "POST":
        backup_service = BackupService()
        settings_obj = LibrarySettings.get_active()

        if settings_obj.backup_enabled:
            valid, error = backup_service.validate_mount()
            if not valid:
                messages.error(request, f"Backup mount error: {error}")
                SystemAlertService.alert_backup_failure(f"Mount unavailable: {error}")
                return redirect("notifications:backup_list")

        try:
            result = backup_service.create_backup()
            if result["success"]:
                messages.success(request, f"Backup created: {result['path']}")
                SystemAlertService.alert_backup_success(result)
            else:
                messages.error(request, f"Backup failed: {result.get('error', 'Unknown error')}")
                SystemAlertService.alert_backup_failure(result.get('error', 'Unknown error'))
        except Exception as e:
            messages.error(request, f"Backup failed: {str(e)}")
            SystemAlertService.alert_backup_failure(str(e))

        return redirect("notifications:backup_list")

    return redirect("notifications:backup_list")


@login_required
@user_passes_test(is_superadmin)
def backup_download(request, filename):
    from .services.backup import BackupService

    if not filename.startswith("library_backup_") or not filename.endswith(".tar.gz"):
        raise Http404("Invalid filename")

    backup_service = BackupService()
    backup_path = backup_service.get_backup_dir() / filename

    if not backup_path.exists():
        raise Http404("Backup not found")

    response = FileResponse(open(backup_path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
