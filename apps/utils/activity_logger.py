from apps.loans.models import ActivityLog


def log_activity(action, description, user):
    """Log an activity to the ActivityLog model.

    Args:
        action: The action type (e.g., ActivityLog.Action.BOOK_CREATED)
        description: Human-readable description of the action
        user: The user who performed the action
    """
    ActivityLog.objects.create(
        action=action,
        description=description,
        user=user
    )
