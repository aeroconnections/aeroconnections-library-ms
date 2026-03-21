# AeroConnections Library Management System

**Version 1.0.0** | A free and open-source library management system built with Django for tracking book inventory and loans.

**License:** AGPL-3.0 - This software is free and any derivative works must also be open source.

## Features

- **Book Inventory** — Add, edit, and track books with unique copy IDs (#01-1, #01-2, etc.)
- **Book Copies** — Each physical book has a unique copy ID for precise tracking
- **Loan Management** — Checkout, return, and configurable loan duration (14-60 days)
- **Days Tracking** — Automatic calculation of days since checkout
- **Overdue Alerts** — Visual indicators for due soon and overdue items
- **Borrower Management** — Add borrowers with activation/deactivation support
- **Return Notes** — Optional notes and damage photos for returns
- **Activity Log** — Immutable record of all system activities
- **Webhook Support** — Configure webhooks for external notifications (Slack, Discord)
- **Email Notifications** — SMTP configuration for email alerts
- **Configurable Settings** — Loan duration, due thresholds, and max books per borrower
- **Staff Authentication** — Secure login with role-based permissions
- **AeroConnections Branding** — Company colors and configurable logo

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for production)

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/library-ms.git
cd library-ms

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

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

### Docker (Production)

```bash
cp .env.example .env
# Edit .env with your settings

docker-compose up -d
```

## Project Structure

```
library-ms/
├── apps/
│   ├── books/              # Book inventory management
│   ├── loans/              # Loan tracking & returns
│   └── notifications/       # Google Chat alerts
├── config/                 # Django settings
├── templates/               # HTML templates
├── static/                  # CSS, JS, logos
├── media/                   # Uploaded images
├── README.md
├── LICENSE                  # AGPL-3.0
└── docker-compose.yml
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

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5 |
| Frontend | TailwindCSS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Task Queue | Celery + Redis |
| Notifications | Google Chat Webhooks |

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.
