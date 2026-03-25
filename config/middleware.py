import time

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "AUTO_LOGOUT_ENABLED", False):
            response = self._handle_auto_logout(request)
            if response is not None:
                return response

        return self.get_response(request)

    def _handle_auto_logout(self, request):
        if self._is_exempt_path(request.path):
            return None

        if not request.user.is_authenticated:
            return None

        now = int(time.time())
        idle_seconds = int(getattr(settings, "AUTO_LOGOUT_IDLE_MINUTES", 10) * 60)
        absolute_seconds = int(getattr(settings, "AUTO_LOGOUT_ABSOLUTE_MINUTES", 60) * 60)

        started_at = request.session.get("session_started_at")
        last_activity = request.session.get("last_activity_at")

        if started_at is None:
            request.session["session_started_at"] = now
            started_at = now

        if last_activity is None:
            request.session["last_activity_at"] = now
            last_activity = now

        if (now - int(started_at)) >= absolute_seconds or (now - int(last_activity)) >= idle_seconds:
            logout(request)
            if self._is_json_request(request):
                return JsonResponse({"detail": "Session expired."}, status=401)
            return redirect(f"{settings.LOGIN_URL}?session_expired=1")

        request.session["last_activity_at"] = now
        return None

    def _is_exempt_path(self, path):
        exempt_prefixes = [
            "/accounts/login/",
            "/accounts/logout/",
            "/admin/login/",
            "/setup/",
            "/static/",
            "/media/",
        ]
        return any(path.startswith(prefix) for prefix in exempt_prefixes)

    def _is_json_request(self, request):
        accept = request.headers.get("Accept", "")
        requested_with = request.headers.get("X-Requested-With", "")
        return "application/json" in accept or requested_with == "XMLHttpRequest" or request.path.startswith("/api/")
