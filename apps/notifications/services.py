import logging
import requests
from django.conf import settings
from django.core.mail import send_mail

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
