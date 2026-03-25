import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.loans.models import ActivityLog, Loan, ReturnNote

from .models import Borrower


def log_activity(action, description, user):
    ActivityLog.objects.create(
        action=action,
        description=description,
        user=user
    )


@login_required
def borrower_list(request):
    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")
    employment_filter = request.GET.get("employment_type")

    borrowers = Borrower.objects.all()

    if status_filter == "active":
        borrowers = borrowers.filter(is_active=True)
    elif status_filter == "inactive":
        borrowers = borrowers.filter(is_active=False)

    if employment_filter:
        borrowers = borrowers.filter(employment_type=employment_filter)

    if search_query:
        borrowers = borrowers.filter(full_name__icontains=search_query) | borrowers.filter(
            email__icontains=search_query
        )

    return render(request, "borrowers/borrower_list.html", {"borrowers": borrowers, "status_filter": status_filter or "active"})


@login_required
def borrower_create(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        employment_type = request.POST.get("employment_type", Borrower.EmploymentType.PERMANENT)
        guardian_name = request.POST.get("guardian_name", "")
        guardian_contact = request.POST.get("guardian_contact", "")

        borrower = Borrower(
            full_name=full_name,
            email=email,
            phone=phone,
            employment_type=employment_type,
            guardian_name=guardian_name,
            guardian_contact=guardian_contact,
        )
        borrower.save()

        log_activity(
            ActivityLog.Action.BORROWER_CREATED,
            f"Borrower '{full_name}' added ({borrower.get_employment_type_display()})",
            request.user
        )
        messages.success(request, f"Borrower '{full_name}' added successfully.")
        return redirect("borrowers:borrower_list_all")

    return render(request, "borrowers/borrower_form.html", {"borrower": None})


@login_required
def borrower_detail(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)
    loans = Loan.objects.filter(borrower_name=borrower.full_name).select_related("book_copy", "created_by").order_by("-checkout_date")
    return_notes = ReturnNote.objects.filter(borrower_name=borrower.full_name).select_related("book_copy", "created_by").order_by("-created_at")
    return render(request, "borrowers/borrower_detail.html", {
        "borrower": borrower,
        "loans": loans,
        "return_notes": return_notes,
    })


@login_required
def borrower_edit(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)

    if request.method == "POST":
        borrower.full_name = request.POST.get("full_name")
        borrower.email = request.POST.get("email")
        borrower.phone = request.POST.get("phone")
        borrower.employment_type = request.POST.get("employment_type", Borrower.EmploymentType.PERMANENT)
        borrower.guardian_name = request.POST.get("guardian_name", "")
        borrower.guardian_contact = request.POST.get("guardian_contact", "")
        borrower.save()

        log_activity(
            ActivityLog.Action.BORROWER_UPDATED,
            f"Borrower '{borrower.full_name}' updated",
            request.user
        )

        messages.success(request, f"Borrower '{borrower.full_name}' updated successfully.")
        return redirect("borrowers:borrower_detail", pk=borrower.pk)

    return render(request, "borrowers/borrower_form.html", {"borrower": borrower})


@login_required
def borrower_deactivate(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)

    if request.method == "POST":
        borrower.is_active = False
        borrower.save()

        log_activity(
            ActivityLog.Action.BORROWER_DEACTIVATED,
            f"Borrower '{borrower.full_name}' deactivated",
            request.user
        )
        messages.success(request, f"Borrower '{borrower.full_name}' deactivated.")
        return redirect("borrowers:borrower_list_all")

    return render(request, "borrowers/borrower_confirm_delete.html", {"borrower": borrower})


@login_required
def borrower_reactivate(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk)

    if request.method == "POST":
        borrower.is_active = True
        borrower.save()

        log_activity(
            ActivityLog.Action.BORROWER_CREATED,
            f"Borrower '{borrower.full_name}' reactivated",
            request.user
        )
        messages.success(request, f"Borrower '{borrower.full_name}' reactivated.")
        return redirect("borrowers:borrower_list_all")

    return render(request, "borrowers/borrower_confirm_reactivate.html", {"borrower": borrower})


@login_required
def borrower_import(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("borrowers:borrower_import")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "File must be a CSV file.")
            return redirect("borrowers:borrower_import")

        decoded_file = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        reader.fieldnames = [fn.strip().lower() for fn in reader.fieldnames]

        required_fields = ["full_name", "email"]
        if not all(field in reader.fieldnames for field in required_fields):
            messages.error(request, f"CSV must have columns: {', '.join(required_fields)}")
            return redirect("borrowers:borrower_import")

        preview_data = {"new": [], "duplicates": [], "errors": []}

        for row_num, row in enumerate(reader, start=2):
            full_name = row.get("full_name", "").strip()
            email = row.get("email", "").strip()
            phone = row.get("phone", "").strip()
            employment_type = row.get("employment_type", "permanent").strip().lower()

            if not full_name or not email:
                preview_data["errors"].append({"row": row_num, "error": "Full name and email are required"})
                continue

            valid_employment_types = ["permanent", "intern", "temporary"]
            if employment_type not in valid_employment_types:
                employment_type = "permanent"

            borrower_data = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "employment_type": employment_type,
                "row": row_num,
            }

            is_duplicate = Borrower.objects.filter(email=email).exists()

            if is_duplicate:
                preview_data["duplicates"].append(borrower_data)
            else:
                preview_data["new"].append(borrower_data)

        return render(request, "borrowers/borrower_import.html", {"preview": preview_data})

    return render(request, "borrowers/borrower_import.html")


@login_required
def borrower_import_confirm(request):
    if request.method == "POST":
        borrowers_data = request.POST.getlist("borrowers_data")
        imported_count = 0

        for borrower_json in borrowers_data:
            try:
                full_name, email, phone, employment_type = borrower_json.split("|")
                borrower = Borrower(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    employment_type=employment_type,
                )
                borrower.save()
                imported_count += 1
            except Exception:
                pass

        if imported_count > 0:
            log_activity(
                ActivityLog.Action.BORROWER_CREATED,
                f"Imported {imported_count} borrower(s) via CSV",
                request.user
            )
            messages.success(request, f"Successfully imported {imported_count} borrower(s).")

        return redirect("borrowers:borrower_list_all")

    return redirect("borrowers:borrower_import")
