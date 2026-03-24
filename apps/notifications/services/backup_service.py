import json
import os
import shutil
import tarfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.utils import timezone


class BackupService:
    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / "data" / "backups"
        self.db_path = settings.DATABASES["default"]["NAME"]
        self.media_path = settings.MEDIA_ROOT

    def _get_settings(self):
        from apps.notifications.models import LibrarySettings
        return LibrarySettings.get_active()

    def get_backup_dir(self):
        settings_obj = self._get_settings()
        if settings_obj and settings_obj.backup_mount_type == 'local':
            return self.backup_dir
        elif settings_obj and settings_obj.backup_mount_type in ['nfs', 'smb']:
            return Path(settings_obj.backup_mount_path) if settings_obj.backup_mount_path else self.backup_dir
        return self.backup_dir

    def validate_mount(self):
        settings_obj = self._get_settings()
        if not settings_obj:
            return True, None

        if not settings_obj.backup_enabled:
            return True, None

        if settings_obj.backup_mount_type == 'local':
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                test_file = self.backup_dir / ".write_test"
                test_file.touch()
                test_file.unlink()
                return True, None
            except Exception as e:
                return False, f"Cannot write to local backup directory: {e}"

        elif settings_obj.backup_mount_type in ['nfs', 'smb']:
            mount_path = settings_obj.backup_mount_path
            if not mount_path:
                return False, "Mount path not configured"

            path = Path(mount_path)
            if not path.exists():
                if settings_obj.backup_mount_type == 'smb':
                    mounted = self._mount_smb(settings_obj)
                    if not mounted:
                        return False, f"Mount path not accessible and SMB mount failed: {mount_path}"
                    path = Path(mount_path)
                else:
                    return False, f"Mount path not accessible: {mount_path}"

            try:
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
                return True, None
            except Exception as e:
                return False, f"Cannot write to mount: {e}"

        return True, None

    def _mount_smb(self, settings_obj):
        try:
            import subprocess

            mount_path = settings_obj.backup_mount_path
            smb_server = settings_obj.smb_server or f"//{settings_obj.smb_server}"
            smb_username = settings_obj.smb_username
            smb_password = settings_obj.smb_password
            smb_domain = settings_obj.smb_domain

            if not smb_server or not smb_username:
                return False

            Path(mount_path).parent.mkdir(parents=True, exist_ok=True)

            mount_options = ["rw", "vers=3.0"]
            if smb_username:
                mount_options.append(f"username={smb_username}")
            if smb_password:
                mount_options.append(f"password={smb_password}")
            if smb_domain:
                mount_options.append(f"domain={smb_domain}")

            cmd = [
                "mount", "-t", "cifs",
                smb_server,
                mount_path,
                "-o", ",".join(mount_options)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def create_backup(self):
        timestamp = timezone.now().strftime("%Y-%m-%d_%H%M%S")
        backup_name = f"library_backup_{timestamp}.tar.gz"
        backup_dir = self.get_backup_dir()

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"success": False, "error": f"Cannot create backup directory: {e}"}

        backup_path = backup_dir / backup_name
        temp_dir = self.backup_dir / f"temp_{timestamp}"
        temp_dir.mkdir(exist_ok=True)

        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, temp_dir / "db.sqlite3")

            if os.path.exists(self.media_path):
                shutil.copytree(self.media_path, temp_dir / "media", dirs_exist_ok=True)

            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(temp_dir, arcname="library_backup")

            size_bytes = os.path.getsize(backup_path)

            metadata = {
                "timestamp": timestamp,
                "created_at": str(timezone.now()),
                "database": str(self.db_path),
                "size_bytes": size_bytes,
            }
            metadata_path = backup_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)

            return {
                "success": True,
                "path": str(backup_path),
                "name": backup_name,
                "size_bytes": size_bytes,
                "timestamp": timestamp,
            }

        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            return {"success": False, "error": str(e)}

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def cleanup_old_backups(self):
        settings_obj = self._get_settings()
        if not settings_obj:
            return []

        retention_days = settings_obj.backup_retention_days
        backup_dir = self.get_backup_dir()
        cutoff = timezone.now() - timezone.timedelta(days=retention_days)

        deleted = []
        for backup_file in backup_dir.glob("library_backup_*.tar.gz"):
            try:
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    backup_file.unlink()
                    metadata_file = backup_file.with_suffix(".json")
                    if metadata_file.exists():
                        metadata_file.unlink()
                    deleted.append(backup_file.name)
            except Exception:
                pass

        return deleted

    def list_backups(self):
        backup_dir = self.get_backup_dir()
        backups = []

        for backup_file in sorted(backup_dir.glob("library_backup_*.tar.gz"), reverse=True):
            try:
                metadata = None
                metadata_file = backup_file.with_suffix(".json")
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)

                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": backup_file.stat().st_size,
                    "created": datetime.fromtimestamp(backup_file.stat().st_mtime, tz=timezone.utc),
                    "metadata": metadata,
                })
            except Exception:
                pass

        return backups

    def get_last_backup_info(self):
        backups = self.list_backups()
        if not backups:
            return None

        last = backups[0]
        age_hours = (timezone.now() - last["created"]).total_seconds() / 3600
        return {
            "created": last["created"],
            "size_bytes": last["size_bytes"],
            "age_hours": round(age_hours, 1),
            "name": last["name"],
        }
