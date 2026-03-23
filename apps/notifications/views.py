from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.loans.services.google_sheets_sync import GoogleSheetsSync


@login_required
def sheets_setup(request):
    sync = GoogleSheetsSync()
    is_authenticated = sync.is_authenticated()
    is_connected = sync.is_connected()
    spreadsheet_url = sync.get_spreadsheet_url()

    context = {
        "is_available": sync.is_available(),
        "is_configured": sync.is_configured(),
        "is_authenticated": is_authenticated,
        "is_connected": is_connected,
        "spreadsheet_id": sync.spreadsheet_id,
        "spreadsheet_url": spreadsheet_url,
    }

    return render(request, "notifications/sheets_setup.html", context)


@login_required
def sheets_auth(request):
    redirect_uri = request.build_absolute_uri(reverse("notifications:sheets_callback"))
    sync = GoogleSheetsSync()
    auth_url, error = sync.get_auth_url(redirect_uri)

    if error:
        messages.error(request, error)
        return redirect("notifications:sheets_setup")

    return redirect(auth_url)


@login_required
def sheets_callback(request):
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error:
        messages.error(request, f"Google OAuth error: {error}")
        return redirect("notifications:sheets_setup")

    if not code:
        messages.error(request, "No authorization code received")
        return redirect("notifications:sheets_setup")

    redirect_uri = request.build_absolute_uri(reverse("notifications:sheets_callback"))
    sync = GoogleSheetsSync()
    success, message = sync.handle_callback(code, redirect_uri)

    if success:
        messages.success(request, "Successfully connected to Google Sheets!")
    else:
        messages.error(request, f"Authentication failed: {message}")

    return redirect("notifications:sheets_setup")


@login_required
def sheets_sync(request):
    sync = GoogleSheetsSync()

    if not sync.is_authenticated():
        messages.error(request, "Not authenticated with Google Sheets")
        return redirect("notifications:sheets_setup")

    if not sync.spreadsheet_id:
        success, message = sync.get_or_create_spreadsheet()
        if success:
            messages.info(request, f"Created new spreadsheet: {message}")
        else:
            messages.error(request, f"Failed to create spreadsheet: {message}")
            return redirect("notifications:sheets_setup")

    results = sync.sync_all()

    success_count = sum(1 for _, (success, _) in results if success)
    error_count = sum(1 for _, (success, _) in results if not success)

    if success_count > 0:
        messages.success(request, f"Synced {success_count} items to Google Sheets")
    if error_count > 0:
        messages.error(request, f"Failed to sync {error_count} items")

    return redirect("notifications:sheets_setup")


@login_required
def sheets_disconnect(request):
    sync = GoogleSheetsSync()
    sync.disconnect()

    messages.success(request, "Disconnected from Google Sheets")
    return redirect("notifications:sheets_setup")
