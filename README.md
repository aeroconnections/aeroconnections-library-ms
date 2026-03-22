# AeroConnections Library Management System

**Version 1.0.5** | A free and open-source library management system built with Django.

**License:** AGPL-3.0 - This software is free and any derivative works must also be open source.

[![Docker Hub](https://img.shields.io/docker/v/sachinaeroconnections/library-ms?label=docker&style=flat-square)](https://hub.docker.com/r/sachinaeroconnections/library-ms)
[![Docker Hub](https://img.shields.io/docker/pulls/sachinaeroconnections/library-ms?style=flat-square)](https://hub.docker.com/r/sachinaeroconnections/library-ms)
[![CI](https://github.com/aeroconnections/library-ms/actions/workflows/CI.yml/badge.svg)](https://github.com/aeroconnections/library-ms/actions/workflows/CI.yml)

## Features

- **Book Copies** — Each physical book has a unique copy ID (e.g., #01-1, #01-2) for precise tracking
- **Loan Management** — Checkout, return, and configurable loan duration (14-60 days)
- **Borrower Management** — Add borrowers with activation/deactivation support
- **Return Notes** — Optional notes and damage photos for returns
- **Activity Log** — Immutable record of all system activities
- **Webhook Support** — Configure webhooks for external notifications (Slack, Discord)
- **Email Notifications** — SMTP configuration for email alerts
- **Google Sheets Backup** — Sync data to Google Sheets for disaster recovery
- **Configurable Settings** — Loan duration, due thresholds, and max books per borrower
- **Modern UI** — Responsive design with AeroConnections branding
- **Multi-platform** — Supports AMD64 and ARM64 architectures

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)

### Docker (Recommended)

```bash
# Pull and run
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  --name library-ms \
  sachinaeroconnections/library-ms:latest

# Or using docker-compose
curl -O https://raw.githubusercontent.com/aeroconnections/library-ms/main/docker-compose.yml
docker-compose up -d
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/aeroconnections/library-ms.git
cd library-ms

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` and login at `http://localhost:8000/admin`

### Test Data

```bash
# Populate test data
python manage.py populate_test_data

# Remove test data
python manage.py remove_test_data
```

## Management Commands

| Command | Description |
|---------|-------------|
| `populate_test_data` | Add sample books, borrowers, and loans |
| `remove_test_data` | Remove all test data (with confirmation) |
| `sync_to_sheets` | Sync data to Google Sheets for backup |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5 |
| Frontend | TailwindCSS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Container | Docker (Alpine-based) |
| Notifications | Webhooks, Email, Google Sheets |

## Project Structure

```
library-ms/
├── apps/
│   ├── books/              # Book & copy management
│   ├── borrowers/          # Borrower management
│   ├── loans/             # Loan tracking & returns
│   └── notifications/      # Settings & branding
├── config/                 # Django settings
├── templates/              # HTML templates
├── static/                 # CSS, JS
├── media/                  # Uploaded images
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── CHANGELOG.md
└── LICENSE (AGPL-3.0)
```

## Loan System

| Days Out | Status | Color |
|----------|--------|-------|
| 0-24 | Active | Gray |
| 25-29 | Due Soon | Amber |
| 30+ | Overdue | Red |

## Documentation

- [Design Documentation](design.md) — Brand guidelines and UI specs
- [Contributing Guide](CONTRIBUTING.md) — How to contribute

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.
