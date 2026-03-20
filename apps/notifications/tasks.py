from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.loans.models import Loan
from .services import NotificationService


@shared_task
def check_overdue_loans():
    overdue_loans = Loan.objects.filter(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    ).exclude(status=Loan.Status.RETURNED).select_related("book")
    
    if overdue_loans.exists():
        return NotificationService.notify_overdue(list(overdue_loans))
    
    return {"chat": False, "count": 0}


@shared_task
def check_due_soon_loans():
    due_soon_loans = Loan.objects.filter(
        status=Loan.Status.ACTIVE,
        checkout_date__lte=timezone.now().date() - timedelta(days=25)
    ).exclude(
        checkout_date__lt=timezone.now().date() - timedelta(days=30)
    ).select_related("book")
    
    if due_soon_loans.exists():
        return NotificationService.notify_due_soon(list(due_soon_loans))
    
    return {"chat": False, "count": 0}


@shared_task
def daily_overdue_check():
    overdue_results = check_overdue_loans()
    due_soon_results = check_due_soon_loans()
    
    return {
        "overdue": overdue_results,
        "due_soon": due_soon_results,
    }
