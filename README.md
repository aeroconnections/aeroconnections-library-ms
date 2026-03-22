# AeroConnections Library Management System

A free and open-source library management system built with Django.

**License:** AGPL-3.0 - This software is free and any derivative works must also be open source.

[![Docker Hub](https://img.shields.io/docker/v/sachinaeroconnections/library-ms?label=docker&style=flat-square)](https://hub.docker.com/r/sachinaeroconnections/library-ms)
[![Docker Hub](https://img.shields.io/docker/pulls/sachinaeroconnections/library-ms?style=flat-square)](https://hub.docker.com/r/sachinaeroconnections/library-ms)

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
- **Setup Wizard** — Easy first-time configuration with PIN protection

## First-Time Setup

### 1. Access the Setup Wizard

After starting the application, navigate to:
```
http://localhost:8000/setup/
```

You will be prompted to enter a Setup PIN. Since this is your first time, you can proceed to the setup wizard directly.

### 2. Configure Your Library

Fill in the setup form with:

| Field | Description |
|-------|-------------|
| Library Name | Your library's name |
| Domain(s) | URL(s) where the app will be accessed. Supports multiple domains separated by commas (e.g., `https://library.com, https://staging.library.com`) |
| Admin Username | Username for the admin account |
| Admin Email | Email for the admin account |
| Admin Password | Password for the admin account |
| Loan Duration | Default loan period in days (default: 30) |
| Due Soon Threshold | Days before due date to show warning (default: 25) |
| Max Books | Maximum books a borrower can have (default: 5) |
| Setup PIN | PIN to access setup page in the future (4-6 digits) |

### 3. Access the Application

After setup, log in at:
```
http://localhost:8000/accounts/login/
```

### Accessing Setup in the Future

To access the setup page after initial configuration:

1. Go to `/setup/`
2. Enter your Setup PIN
3. You can change settings or reset configurations

## Deployment

### Docker (Recommended)

```bash
# Pull and run
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e ALLOWED_HOSTS="*" \
  -e CSRF_TRUSTED_ORIGINS="https://your-domain.com,http://localhost:8000" \
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

# Start development server
python manage.py runserver
```

Then access `/setup/` to configure your library.

## Troubleshooting

### CSRF Verification Failed (403 Error)

If you see a `403 Forbidden - CSRF verification failed` error when accessing the application from a domain other than localhost, you need to add your domain to `CSRF_TRUSTED_ORIGINS`.

**Option 1: Quick Fix with Environment Variable**

```bash
docker stop library-ms
docker rm library-ms
docker run -d \
  --name library-ms \
  -e "CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://your-domain.com" \
  -p 8000:8000 \
  -v library-data:/app/data \
  sachinaeroconnections/library-ms:latest
```

For docker-compose, add to your service:
```yaml
environment:
  - CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://your-domain.com
```

**Option 2: Update Domain in Database (Recommended)**

If you've already completed the setup wizard, you can update your domain directly in the database:

```bash
# Enter the container shell
docker exec -it library-ms python manage.py shell
```

Then run these commands:

```python
# View current domain
from apps.setup.models import SetupConfig
c = SetupConfig.objects.first()
print(f"Current domain: {c.domain}")

# Update domain (single domain)
c.domain = 'https://your-domain.com'
c.save()

# Update domain (multiple domains)
c.domain = 'https://your-domain.com, https://staging.your-domain.com'
c.save()

# Verify
print(f"New domain: {c.domain}")
```

Or in a single command:

```bash
docker exec -it library-ms python manage.py shell -c "
from apps.setup.models import SetupConfig
c = SetupConfig.objects.first()
c.domain = 'https://your-domain.com'
c.save()
print('Domain updated to:', c.domain)
"
```

After updating the domain, restart the container:
```bash
docker restart library-ms
```

### View Current CSRF Trusted Origins

To check which origins are currently trusted:

```bash
docker exec -it library-ms python manage.py shell -c "from django.conf import settings; print('Trusted origins:', settings.CSRF_TRUSTED_ORIGINS)"
```

### Reset Setup Configuration

To reset the setup configuration and run the wizard again:

```bash
docker exec -it library-ms python manage.py shell -c "
from apps.setup.models import SetupConfig
SetupConfig.objects.all().delete()
print('Setup configuration deleted. Access /setup/ to reconfigure.')
"

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
│   ├── notifications/      # Settings & branding
│   └── setup/            # Setup wizard & configuration
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
