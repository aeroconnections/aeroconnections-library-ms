import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_email(subject: str, message: str, recipient_list: list[str]) -> bool:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient_list}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    @staticmethod
    def send_google_chat_message(message: str, webhook_url: str = None) -> bool:
        webhook_url = webhook_url or settings.GOOGLE_CHAT_WEBHOOK_URL

        if not webhook_url:
            logger.warning("Google Chat webhook URL not configured")
            return False

        try:
            payload = {"text": message}
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            logger.info("Google Chat message sent successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send Google Chat message: {e}")
            return False

    @staticmethod
    def notify_overdue(loans: list) -> dict:
        if not loans:
            return {"chat": False, "count": 0}

        message_lines = [
            ":warning: *Overdue Books Alert*",
            "",
            f"*Total Overdue:* {len(loans)}",
            "",
        ]

        for loan in loans[:10]:
            message_lines.append(f"• #{loan.book_id_snapshot} - {loan.borrower_name} ({loan.days_out} days)")

        if len(loans) > 10:
            message_lines.append(f"...and {len(loans) - 10} more")

        message_lines.append("")
        message_lines.append("Please follow up with borrowers.")

        message = "\n".join(message_lines)
        success = NotificationService.send_google_chat_message(message)

        return {"chat": success, "count": len(loans)}

    @staticmethod
    def notify_due_soon(loans: list) -> dict:
        if not loans:
            return {"chat": False, "count": 0}

        message_lines = [
            ":alarm_clock: *Books Due Soon (25+ days)*",
            "",
            f"*Total Due Soon:* {len(loans)}",
            "",
        ]

        for loan in loans[:10]:
            message_lines.append(f"• #{loan.book_id_snapshot} - {loan.borrower_name} ({loan.days_out} days)")

        if len(loans) > 10:
            message_lines.append(f"...and {len(loans) - 10} more")

        message = "\n".join(message_lines)
        success = NotificationService.send_google_chat_message(message)

        return {"chat": success, "count": len(loans)}


class SystemAlertService:
    @staticmethod
    def send_alert(level: str, title: str, message: str) -> bool:
        from apps.notifications.models import LibrarySettings

        settings_obj = LibrarySettings.get_active()
        if not settings_obj or not settings_obj.system_alert_enabled:
            return False

        webhook_url = settings_obj.system_alert_webhook_url
        if not webhook_url:
            return False

        emoji = {
            "info": ":information_source:",
            "warning": ":warning:",
            "error": ":x:",
            "critical": ":fire:",
        }.get(level, ":bell:")

        message_lines = [
            f"{emoji} *{title}*",
            "",
            message,
            "",
            f"Sent: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        full_message = "\n".join(message_lines)

        try:
            payload = {"text": full_message}
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"System alert sent: {title}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send system alert: {e}")
            return False

    @staticmethod
    def alert_backup_success(backup_info: dict):
        size_mb = backup_info.get("size_bytes", 0) / 1024 / 1024
        message = (
            f"Backup created successfully\n\n"
            f"File: {backup_info.get('name', 'Unknown')}\n"
            f"Size: {size_mb:.2f} MB\n"
            f"Path: {backup_info.get('path', 'Unknown')}"
        )
        return SystemAlertService.send_alert("info", "Library Backup Complete", message)

    @staticmethod
    def alert_backup_failure(error: str):
        message = f"Backup failed with error:\n\n{error}"
        return SystemAlertService.send_alert("error", "Library Backup Failed", message)

    @staticmethod
    def alert_mount_unavailable(mount_type: str, path: str):
        message = (
            f"Backup is enabled but mount is unavailable.\n\n"
            f"Type: {mount_type}\n"
            f"Path: {path}\n\n"
            f"Please check your backup configuration."
        )
        return SystemAlertService.send_alert("warning", "Backup Mount Unavailable", message)
