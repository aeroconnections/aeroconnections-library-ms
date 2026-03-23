# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.5] - 2026-03-23

### Fixed
- **OAuth HTTPS Detection** - Added `SECURE_PROXY_SSL_HEADER` for HTTPS detection behind proxies (Tailscale, Cloudflare, etc.)
- **OAuth State Handling** - Fixed state validation and authorization_response URL for proper OAuth flow

### Added
- **App Version Footer** - Version number displayed in footer on all pages
- **Repository Links** - GitHub and Docker Hub links in footer
- **Settings Navbar Link** - Settings page accessible from navbar (superadmin only)

## [1.2.4] - 2026-03-23

### Added
- **Settings Navbar Link** - Settings page accessible from navbar (superadmin only)
- **google-auth-oauthlib** - Added package for OAuth authentication

## [1.2.3] - 2026-03-23

### Added
- **Browser-Based Google Sheets OAuth** - No more manual file copying; authorize directly from browser
- **Auto-Sync on Activity** - Data syncs automatically on book/borrower/loan changes
- **First-Time Sync** - "Create Spreadsheet & Sync All Data" button for initial backup
- **Google Sheets Settings Page** - Dedicated UI at `/settings/sheets/`

### Changed
- **Credentials Storage** - OAuth credentials stored in `/app/data/` for Docker volume persistence

## [1.2.2] - 2026-03-23

### Fixed
- **Borrower Detail** - Fixed FieldError when viewing borrower with loans
- **Borrower Tabs** - Added Active/All/Inactive tabs for better filtering

### Added
- **Editable Checkout Date** - Staff can now set a custom checkout date when creating loans, enabling adding of historical records

## [1.2.1] - 2026-03-23

### Fixed
- **Data Persistence** - Database now stored at `/app/data/` for proper Docker volume mounting
- **Clear All Data Command** - New management command to reset database completely

## [1.2.0] - 2026-03-23

### Added
- **CSV Import - Books** - Bulk import books via CSV file with preview and duplicate detection
- **CSV Import - Borrowers** - Bulk import borrowers via CSV file with preview and duplicate detection
- **Book Search Autocomplete** - Search existing books when adding new books to auto-fill author and ISBN

### Fixed
- **Book Edit** - Copies field now auto-fills with current count to prevent ValueError

## [1.1.0] - 2026-03-22

### Added
- **Setup Wizard** - Guided first-time setup for library name, admin account, and branding
- **PIN Protection** - Setup wizard secured with a 4-digit PIN
- **CSRF_TRUSTED_ORIGINS** - Docker environment variable for domain-based access
- **Setup Security Page** - Change PIN after initial setup

## [1.0.0] - 2026-03-22

### Added
- **Book Copy System** - Each physical book has a unique copy ID (e.g., #01-1, #01-2) for precise tracking
- **Borrower Management** - Full CRUD operations with activation/deactivation support
- **Return Notes** - Optional notes and damage photos attached to returns
- **Activity Log** - Immutable record of all system activities (checkouts, returns, etc.)
- **Configurable Loan Settings** - Adjustable loan duration (14-60 days) and due thresholds
- **Webhook Support** - Configure external webhooks for notifications
- **Email Notifications** - SMTP configuration for email alerts
- **Library Settings** - Admin-configurable settings for loans, notifications, and integrations
- **Modern UI** - Top navigation bar with responsive design and AeroConnections branding
- **Google Sheets Backup** - Sync data to Google Sheets for disaster recovery
- **Test Data Management** - Commands to add/remove test data

### Changed
- **Loan System** - Now links to specific BookCopy instead of Book
- **Dashboard** - Shows book titles with copy IDs for better tracking
- **UI/UX** - Complete redesign with horizontal top navigation

### Fixed
- **Return Notes** - No longer saved when empty
- **Branding** - Company name and library name toggles now work correctly
- **Dashboard** - Copy IDs display correctly in overdue/due soon sections
