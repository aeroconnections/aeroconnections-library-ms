# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
