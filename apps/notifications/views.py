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
    auth_url, error, flow_json = sync.create_flow(redirect_uri)

    if error:
        messages.error(request, error)
        return redirect("notifications:sheets_setup")

    request.session["oauth_flow_json"] = flow_json

    return redirect(auth_url)


@login_required
def sheets_callback(request):
    error = request.GET.get("error")
    if error:
        messages.error(request, f"Google OAuth error: {error}")
        return redirect("notifications:sheets_setup")

    authorization_response = request.build_absolute_uri(request.get_full_path())
    flow_json = request.session.pop("oauth_flow_json", None)

    if not flow_json:
        messages.error(request, "OAuth session expired. Please try again.")
        return redirect("notifications:sheets_setup")

    sync = GoogleSheetsSync()
    success, message = sync.handle_callback_flow(authorization_response, flow_json)

    if success:
        messages.success(request, "Successfully connected to Google Sheets!")
    else:
        messages.error(request, f"Authentication failed: {message}")

    return redirect("notifications:sheets_setup")


@login_required
def sheets_auth_console(request):
    redirect_uri = request.build_absolute_uri(reverse("notifications:sheets_callback_console"))
    sync = GoogleSheetsSync()
    auth_url, error, flow_json = sync.create_flow(redirect_uri)

    if error:
        messages.error(request, error)
        return redirect("notifications:sheets_setup")

    request.session["oauth_console_flow_json"] = flow_json

    context = {"auth_url": auth_url}
    return render(request, "notifications/sheets_auth_console.html", context)


@login_required
def sheets_callback_console(request):
    error = request.GET.get("error")
    if error:
        messages.error(request, f"Google OAuth error: {error}")
        return redirect("notifications:sheets_setup")

    flow_json = request.session.pop("oauth_console_flow_json", None)
    redirect_uri = request.build_absolute_uri(reverse("notifications:sheets_callback_console"))

    if not flow_json:
        messages.error(request, "OAuth session expired. Please try again.")
        return redirect("notifications:sheets_setup")

    if request.method == "GET":
        code = request.GET.get("code")
        if not code:
            messages.error(request, "No authorization code received")
            return redirect("notifications:sheets_setup")

        sync = GoogleSheetsSync()
        success, message = sync.exchange_code(code, redirect_uri, flow_json)

        if success:
            messages.success(request, "Successfully connected to Google Sheets!")
        else:
            messages.error(request, f"Authentication failed: {message}")

        return redirect("notifications:sheets_setup")

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        if not code:
            messages.error(request, "Please enter the authorization code")
            return redirect("notifications:sheets_auth_console")

        sync = GoogleSheetsSync()
        success, message = sync.exchange_code(code, redirect_uri, flow_json)

        if success:
            messages.success(request, "Successfully connected to Google Sheets!")
        else:
            messages.error(request, f"Authentication failed: {message}")

        return redirect("notifications:sheets_setup")

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
