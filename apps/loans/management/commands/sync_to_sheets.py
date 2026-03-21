from django.core.management.base import BaseCommand

from apps.loans.services.google_sheets_sync import GoogleSheetsSync


class Command(BaseCommand):
    help = "Sync library data to Google Sheets for backup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--auth-only",
            action="store_true",
            help="Only authenticate without syncing",
        )

    def handle(self, *args, **options):
        self.stdout.write("Google Sheets Sync\n" + "=" * 30)

        sync = GoogleSheetsSync()

        success, message = sync.authenticate()
        if not success:
            self.stdout.write(self.style.WARNING(f"Authentication failed: {message}"))
            self.stdout.write("\nSetup instructions:")
            self.stdout.write("1. Create a project at https://console.cloud.google.com")
            self.stdout.write("2. Enable Google Sheets API")
            self.stdout.write("3. Create OAuth credentials (Desktop app)")
            self.stdout.write("4. Save as 'sheets_credentials.json' in project root")
            self.stdout.write("5. Run this command again")
            return

        self.stdout.write(self.style.SUCCESS(f"✓ {message}"))

        if options["auth_only"]:
            return

        if not sync.spreadsheet_id:
            spreadsheet_id, msg = sync.get_or_create_spreadsheet()
            if spreadsheet_id:
                self.stdout.write(self.style.SUCCESS(f"✓ {msg}"))
                self.stdout.write(f"  URL: {sync.get_spreadsheet_url()}")
            else:
                self.stdout.write(self.style.WARNING(f"Spreasheet error: {msg}"))

        results = sync.sync_all()

        self.stdout.write("")
        for name, (success, message) in results:
            if success:
                self.stdout.write(self.style.SUCCESS(f"✓ {name}: {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {name}: {message}"))

        if sync.spreadsheet_id:
            self.stdout.write("")
            self.stdout.write(f"Spreadsheet URL: {sync.get_spreadsheet_url()}")
