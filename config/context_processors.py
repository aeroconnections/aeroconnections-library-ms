from django.conf import settings


def app_context(request):
    return {
        "APP_VERSION": getattr(settings, "APP_VERSION", "Unknown"),
        "GITHUB_REPO": getattr(settings, "GITHUB_REPO", ""),
        "DOCKERHUB_REPO": getattr(settings, "DOCKERHUB_REPO", ""),
        "AUTO_LOGOUT_ENABLED": getattr(settings, "AUTO_LOGOUT_ENABLED", False),
        "AUTO_LOGOUT_IDLE_SECONDS": int(getattr(settings, "AUTO_LOGOUT_IDLE_MINUTES", 10) * 60),
        "AUTO_LOGOUT_WARNING_SECONDS": getattr(settings, "AUTO_LOGOUT_WARNING_SECONDS", 60),
    }
