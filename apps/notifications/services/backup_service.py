import json
import os
import shutil
import subprocess
import tarfile
from datetime import datetime
from datetime import timezone as dt_timezone
from pathlib import Path

from django.conf import settings
from django.utils import timezone


class BackupService:
    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / "data" / "backups"
        self.temp_root = Path("/tmp") / "library-backups"
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
            mount_path = settings_obj.backup_mount_path or ""
            if settings_obj.backup_mount_type == 'smb' and self._is_remote_path(mount_path):
                return Path("/mnt/backups")
            return Path(mount_path) if mount_path else self.backup_dir
        return self.backup_dir

    @staticmethod
    def _is_remote_path(path_value):
        value = (path_value or "").strip()
        return value.startswith("smb://") or value.startswith("//")

    @staticmethod
    def _extract_share_from_remote(remote_path):
        value = (remote_path or "").strip()
        if value.startswith("smb://"):
            value = value[len("smb://"):]
        value = value.strip("/")
        parts = value.split("/", 1)
        if len(parts) > 1:
            return parts[1]
        return ""

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

            remote_hint = ""
            local_mount_path = mount_path
            if settings_obj.backup_mount_type == 'smb' and self._is_remote_path(mount_path):
                remote_hint = mount_path
                local_mount_path = "/mnt/backups"

            path = Path(local_mount_path)
            if settings_obj.backup_mount_type == 'smb':
                path.mkdir(parents=True, exist_ok=True)
                if not os.path.ismount(path):
                    if not self._allow_in_container_mount():
                        return False, (
                            "SMB path is not mounted in container. "
                            "In Dockhand, mount SMB on host and bind it to this container path "
                            f"({path}). Set ALLOW_IN_CONTAINER_SMB_MOUNT=true only if privileged mounts are enabled."
                        )

                    mounted, mount_error = self._mount_smb(settings_obj, str(path), remote_hint)
                    if not mounted:
                        return False, f"SMB mount failed for {settings_obj.smb_server or remote_hint or mount_path}: {mount_error}"
                if not os.path.ismount(path):
                    return False, f"SMB path is not mounted: {path}"
            elif not path.exists():
                return False, f"Mount path not accessible: {mount_path}"

            try:
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
                return True, None
            except Exception as e:
                return False, f"Cannot write to mount: {e}"

        return True, None

    @staticmethod
    def _allow_in_container_mount():
        return os.environ.get("ALLOW_IN_CONTAINER_SMB_MOUNT", "false").lower() == "true"

    def _load_smb_credentials_from_secret(self):
        secret_candidates = [
            os.environ.get("SMB_CREDENTIALS_FILE"),
            "/run/secrets/smb-credentials",
            "/run/secrets/smb_credentials",
            str(Path(settings.BASE_DIR) / "secrets" / "smb-credentials.env"),
        ]

        creds = {}
        for candidate in secret_candidates:
            if not candidate:
                continue

            secret_path = Path(candidate)
            if not secret_path.exists():
                continue

            for line in secret_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                creds[key.strip()] = value.strip()

            if creds:
                return {
                    "username": creds.get("SMB_USERNAME", ""),
                    "password": creds.get("SMB_PASSWORD", ""),
                    "domain": creds.get("SMB_DOMAIN", ""),
                }

        return {"username": "", "password": "", "domain": ""}

    @staticmethod
    def _normalize_smb_source(smb_server, mount_path, remote_hint=""):
        raw = (smb_server or "").strip()
        hint_share = BackupService._extract_share_from_remote(remote_hint)
        if raw.startswith("smb://"):
            raw = raw[len("smb://"):]
        raw = raw.strip("/")

        if raw.startswith("//"):
            raw = raw[2:]

        parts = raw.split("/", 1)
        host = parts[0] if parts and parts[0] else ""
        share = parts[1] if len(parts) > 1 and parts[1] else ""

        if not share and hint_share:
            share = hint_share

        if not share:
            share = Path(mount_path).name

        if not host or not share:
            return ""

        return f"//{host}/{share}"

    def _mount_smb(self, settings_obj, mount_path, remote_hint=""):
        try:
            smb_source = self._normalize_smb_source(settings_obj.smb_server, mount_path, remote_hint)
            secret_creds = self._load_smb_credentials_from_secret()

            smb_username = settings_obj.smb_username or secret_creds["username"]
            smb_password = settings_obj.smb_password or secret_creds["password"]
            smb_domain = settings_obj.smb_domain or secret_creds["domain"]

            if not smb_source:
                return False, "Invalid SMB server/share. Use smb://host/share or //host/share"
            if not smb_username:
                return False, "SMB username not configured (UI or secrets file)"

            Path(mount_path).mkdir(parents=True, exist_ok=True)

            mount_options = ["rw", "vers=3.0"]
            if smb_username:
                mount_options.append(f"username={smb_username}")
            if smb_password:
                mount_options.append(f"password={smb_password}")
            if smb_domain:
                mount_options.append(f"domain={smb_domain}")

            cmd = [
                "mount", "-t", "cifs",
                smb_source,
                mount_path,
                "-o", ",".join(mount_options)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                stdout = (result.stdout or "").strip()
                details = stderr or stdout or "Unknown mount error"
                if "permission denied" in details.lower():
                    details += " (container may need privileged mount capability)"
                return False, details

            return True, None
        except Exception as e:
            return False, str(e)

    def create_backup(self):
        timestamp = timezone.now().strftime("%Y-%m-%d_%H%M%S")
        backup_name = f"library_backup_{timestamp}.tar.gz"
        backup_dir = self.get_backup_dir()

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"success": False, "error": f"Cannot create backup directory: {e}"}

        backup_path = backup_dir / backup_name
        self.temp_root.mkdir(parents=True, exist_ok=True)
        temp_dir = self.temp_root / f"temp_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)

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
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=dt_timezone.utc)
                if mtime < cutoff:
                    backup_file.unlink()
                    metadata_file = backup_file.with_suffix(".json")
                    if metadata_file.exists():
                        metadata_file.unlink()
                    deleted.append(backup_file.name)
            except Exception:
                continue

        return deleted

    def list_backups_with_diagnostics(self):
        backup_dir = self.get_backup_dir()
        backups = []
        skipped = []

        if not backup_dir.exists():
            return backups, {
                "backup_dir": str(backup_dir),
                "discovered": 0,
                "displayed": 0,
                "skipped": [],
            }

        discovered_files = sorted(backup_dir.glob("library_backup_*.tar.gz"), reverse=True)

        for backup_file in discovered_files:
            try:
                metadata = None
                metadata_file = backup_file.with_suffix(".json")
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                    except Exception as e:
                        skipped.append({
                            "name": metadata_file.name,
                            "error": f"metadata parse failed: {e}",
                        })

                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": backup_file.stat().st_size,
                    "created": datetime.fromtimestamp(backup_file.stat().st_mtime, tz=dt_timezone.utc),
                    "metadata": metadata,
                })
            except Exception as e:
                skipped.append({
                    "name": backup_file.name,
                    "error": str(e),
                })
                continue

        diagnostics = {
            "backup_dir": str(backup_dir),
            "discovered": len(discovered_files),
            "displayed": len(backups),
            "skipped": skipped,
        }

        return backups, diagnostics

    def list_backups(self):
        backups, _ = self.list_backups_with_diagnostics()
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
