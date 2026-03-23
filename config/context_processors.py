from django.conf import settings


def app_context(request):
    return {
        "APP_VERSION": getattr(settings, "APP_VERSION", "Unknown"),
        "GITHUB_REPO": getattr(settings, "GITHUB_REPO", ""),
        "DOCKERHUB_REPO": getattr(settings, "DOCKERHUB_REPO", ""),
    }
