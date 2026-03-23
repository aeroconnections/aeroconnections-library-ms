import logging
import os
from datetime import datetime

from django.conf import settings

logger = logging.getLogger(__name__)

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

    def __init__(self):
        self.service = None
        self.credentials = None
        self.spreadsheet_id = None
        self._load_spreadsheet_id()

    def _load_spreadsheet_id(self):
        try:
            from apps.notifications.models import LibrarySettings

            settings_obj = LibrarySettings.get_active()
            if settings_obj and settings_obj.google_sheets_id:
                self.spreadsheet_id = settings_obj.google_sheets_id
        except Exception:
            pass

    def _get_credentials_path(self):
        return os.path.join(settings.BASE_DIR, "data", "sheets_credentials.json")

    def _get_token_path(self):
        return os.path.join(settings.BASE_DIR, "data", "sheets_token.json")

    def _ensure_data_dir(self):
        data_dir = os.path.join(settings.BASE_DIR, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    def is_available(self):
        return GOOGLE_SHEETS_AVAILABLE

    def is_configured(self):
        return os.path.exists(self._get_credentials_path())

    def is_authenticated(self):
        if not self.is_configured():
            return False

        try:
            creds = None
            token_path = self._get_token_path()
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

            if creds and creds.valid:
                self.credentials = creds
                self.service = build("sheets", "v4", credentials=creds)
                return True

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
                self.credentials = creds
                self.service = build("sheets", "v4", credentials=creds)
                return True
        except Exception:
            pass

        return False

    def is_connected(self):
        return self.is_authenticated() and self.spreadsheet_id

    def get_auth_url(self, redirect_uri):
        if not GOOGLE_SHEETS_AVAILABLE:
            return None, "Google API client not installed", None

        credentials_path = self._get_credentials_path()
        if not os.path.exists(credentials_path):
            return None, f"Credentials file not found: {credentials_path}"

        try:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
            flow.redirect_uri = redirect_uri
            auth_url, state = flow.authorization_url(
                prompt="consent", 
                access_type="offline",
                include_granted_scopes="true"
            )
            return auth_url, None, state
        except Exception as e:
            return None, str(e), None

    def handle_callback(self, authorization_response_url):
        if not GOOGLE_SHEETS_AVAILABLE:
            return False, "Google API client not installed"

        credentials_path = self._get_credentials_path()
        if not os.path.exists(credentials_path):
            return False, f"Credentials file not found: {credentials_path}"

        try:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
            self.credentials = flow.fetch_token(authorization_response=authorization_response_url)

            self._ensure_data_dir()
            token_path = self._get_token_path()
            with open(token_path, "w") as token:
                token.write(self.credentials.to_json())

            self.service = build("sheets", "v4", credentials=self.credentials)
            return True, "Authentication successful"
        except Exception as e:
            return False, str(e)

    def save_credentials(self, credentials_json):
        try:
            self._ensure_data_dir()
            token_path = self._get_token_path()
            with open(token_path, "w") as f:
                f.write(credentials_json)
            return self.is_authenticated()
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False

    def authenticate(self):
        if not GOOGLE_SHEETS_AVAILABLE:
            return False, "Google API client not installed. Run: pip install google-api-python-client google-auth"

        credentials_path = self._get_credentials_path()
        if not os.path.exists(credentials_path):
            return False, f"Credentials file not found: {credentials_path}"

        creds = None
        token_path = self._get_token_path()
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build("sheets", "v4", credentials=creds)
        return True, "Authenticated successfully"

    def disconnect(self):
        token_path = self._get_token_path()
        if os.path.exists(token_path):
            os.remove(token_path)
        self.service = None
        self.credentials = None
        return True

    def get_or_create_spreadsheet(self, title=None):
        if not self.is_authenticated():
            return None, "Not authenticated"

        if self.spreadsheet_id:
            return self.spreadsheet_id, "Using existing spreadsheet"

        title = title or f"Library Backup {datetime.now().strftime('%Y-%m-%d')}"

        spreadsheet = {
            "properties": {"title": title},
            "sheets": [
                {"properties": {"title": "Books"}},
                {"properties": {"title": "Copies"}},
                {"properties": {"title": "Borrowers"}},
                {"properties": {"title": "Loans"}},
            ],
        }

        spreadsheet = (
            self.service.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )

        self.spreadsheet_id = spreadsheet.get("spreadsheetId")
        self._save_spreadsheet_id()
        return self.spreadsheet_id, f"Created new spreadsheet: {self.spreadsheet_id}"

    def _save_spreadsheet_id(self):
        try:
            from apps.notifications.models import LibrarySettings

            settings_obj = LibrarySettings.get_active()
            if settings_obj:
                settings_obj.google_sheets_id = self.spreadsheet_id
                settings_obj.save()
        except Exception:
            pass

    def clear_sheet(self, sheet_name):
        if not self.is_authenticated() or not self.spreadsheet_id:
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
        if not self.is_authenticated() or not self.spreadsheet_id:
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

        if self.spreadsheet_id and self.is_authenticated():
            results.append(("Books", self.sync_books()))
            results.append(("Copies", self.sync_copies()))
            results.append(("Borrowers", self.sync_borrowers()))
            results.append(("Loans", self.sync_loans()))

        return results

    def get_spreadsheet_url(self):
        if self.spreadsheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
        return None


def auto_sync():
    if not GOOGLE_SHEETS_AVAILABLE:
        return

    try:
        sync = GoogleSheetsSync()
        if sync.is_connected():
            sync.sync_all()
            logger.info("Auto-sync completed successfully")
        elif sync.is_authenticated() and not sync.spreadsheet_id:
            sync.get_or_create_spreadsheet()
            sync.sync_all()
            logger.info("Auto-sync: created spreadsheet and synced all data")
    except Exception as e:
        logger.error(f"Auto-sync failed: {e}")
