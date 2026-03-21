import os
from datetime import datetime

from django.conf import settings

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False


class GoogleSheetsSync:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    TOKEN_PATH = "sheets_token.json"
    CREDENTIALS_PATH = os.path.join(settings.BASE_DIR, "sheets_credentials.json")

    def __init__(self):
        self.service = None
        self.credentials = None
        self.spreadsheet_id = getattr(settings, "GOOGLE_SHEETS_ID", None)
        if not self.spreadsheet_id:
            try:
                from apps.notifications.models import LibrarySettings
                settings_obj = LibrarySettings.get_active()
                if settings_obj and settings_obj.google_sheets_id:
                    self.spreadsheet_id = settings_obj.google_sheets_id
            except Exception:
                pass

    def authenticate(self):
        if not GOOGLE_SHEETS_AVAILABLE:
            return False, "Google API client not installed. Run: pip install google-api-python-client google-auth"

        if not os.path.exists(self.CREDENTIALS_PATH):
            return False, f"Credentials file not found: {self.CREDENTIALS_PATH}"

        creds = None
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_PATH, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build("sheets", "v4", credentials=creds)
        return True, "Authenticated successfully"

    def get_or_create_spreadsheet(self, title=None):
        if not self.service:
            return None, "Not authenticated"

        if self.spreadsheet_id:
            return self.spreadsheet_id, "Using existing spreadsheet"

        title = title or f"Library Backup {datetime.now().strftime('%Y-%m-%d')}"

        spreadsheet = {
            "properties": {"title": title},
            "sheets": [
                {
                    "properties": {"title": "Books"},
                    "data": {"rowData": []},
                },
                {
                    "properties": {"title": "Copies"},
                    "data": {"rowData": []},
                },
                {
                    "properties": {"title": "Borrowers"},
                    "data": {"rowData": []},
                },
                {
                    "properties": {"title": "Loans"},
                    "data": {"rowData": []},
                },
            ],
        }

        spreadsheet = (
            self.service.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )

        self.spreadsheet_id = spreadsheet.get("spreadsheetId")
        return self.spreadsheet_id, f"Created new spreadsheet: {self.spreadsheet_id}"

    def clear_sheet(self, sheet_name):
        if not self.service or not self.spreadsheet_id:
            return False, "Not connected"

        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:Z",
                body={},
            ).execute()
            return True, f"Cleared {sheet_name}"
        except HttpError as e:
            return False, str(e)

    def update_sheet(self, sheet_name, data):
        if not self.service or not self.spreadsheet_id:
            return False, "Not connected"

        try:
            self.clear_sheet(sheet_name)

            values = [data]
            body = {"values": values}

            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()

            return True, f"Updated {sheet_name} with {len(data)} rows"
        except HttpError as e:
            return False, str(e)

    def sync_books(self):
        from apps.books.models import Book

        books = Book.objects.all().order_by("book_id")
        data = [["Book ID", "Title", "Author", "ISBN", "Created At"]]

        for book in books:
            data.append(
                [
                    book.book_id,
                    book.title,
                    book.author,
                    book.isbn,
                    book.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return self.update_sheet("Books", data)

    def sync_copies(self):
        from apps.books.models import BookCopy

        copies = BookCopy.objects.select_related("book").all().order_by("copy_id")
        data = [["Copy ID", "Book ID", "Book Title", "Status", "Condition", "Created At"]]

        for copy in copies:
            data.append(
                [
                    copy.copy_id,
                    copy.book.book_id,
                    copy.book.title,
                    copy.get_status_display(),
                    copy.condition or "",
                    copy.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return self.update_sheet("Copies", data)

    def sync_borrowers(self):
        from apps.borrowers.models import Borrower

        borrowers = Borrower.objects.all().order_by("full_name")
        data = [
            [
                "ID",
                "Full Name",
                "Email",
                "Phone",
                "Employment Type",
                "Active",
                "Created At",
            ]
        ]

        for borrower in borrowers:
            data.append(
                [
                    borrower.id,
                    borrower.full_name,
                    borrower.email,
                    borrower.phone,
                    borrower.get_employment_type_display(),
                    "Yes" if borrower.is_active else "No",
                    borrower.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return self.update_sheet("Borrowers", data)

    def sync_loans(self):
        from apps.loans.models import Loan

        loans = Loan.objects.select_related("book_copy", "book_copy__book").all().order_by("-created_at")
        data = [
            [
                "ID",
                "Copy ID",
                "Book Title",
                "Borrower",
                "Checkout Date",
                "Due Date",
                "Return Date",
                "Status",
                "Notes",
                "Created At",
            ]
        ]

        for loan in loans:
            data.append(
                [
                    loan.id,
                    loan.copy_id_snapshot,
                    loan.book_title_snapshot,
                    loan.borrower_name,
                    loan.checkout_date.strftime("%Y-%m-%d"),
                    loan.due_date.strftime("%Y-%m-%d"),
                    loan.return_date.strftime("%Y-%m-%d") if loan.return_date else "",
                    loan.get_status_display(),
                    loan.notes or "",
                    loan.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return self.update_sheet("Loans", data)

    def sync_all(self):
        results = []

        results.append(("Spreadsheet", self.get_or_create_spreadsheet()))

        if self.spreadsheet_id:
            results.append(("Books", self.sync_books()))
            results.append(("Copies", self.sync_copies()))
            results.append(("Borrowers", self.sync_borrowers()))
            results.append(("Loans", self.sync_loans()))

        return results

    def get_spreadsheet_url(self):
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None
