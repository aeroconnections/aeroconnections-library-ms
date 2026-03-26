# Contributing to Library Management System

Thank you for your interest in contributing! This project is open source and we welcome contributions from the community.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We expect all participants to uphold a respectful and inclusive environment.

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- Docker & Docker Compose (optional, for containerized development)

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/library-ms.git
   cd library-ms
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Running Tests

```bash
python manage.py test
```

### Code Quality

We use ruff to maintain code quality:

```bash
# Lint code
ruff check .
```

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/add-book-categories
# or
git checkout -b fix/loan-date-validation
```

Branch naming conventions:
- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation
- `refactor/` — Code refactoring
- `test/` — Adding or updating tests

### 2. Make Your Changes

- Write clean, readable code following existing patterns
- Add tests for new functionality
- Update documentation as needed
- Follow the style guidelines below

### 3. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add book category filtering
fix: correct loan due date calculation
docs: update API documentation
refactor: simplify notification service
test: add tests for overdue alerts
```

### 4. Push Your Changes

```bash
git push origin feature/add-book-categories
```

### 5. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:
   - **Description**: What does this PR do?
   - **Type**: Bug fix, feature, documentation, etc.
   - **Related Issues**: Link any related issues
   - **Testing**: How was this tested?

## Pull Request Guidelines

- PRs should be focused and atomic (one feature/fix per PR)
- All tests must pass before merging
- Code must pass linting checks
- Update documentation for any user-facing changes
- Add/update tests for new functionality
- Keep PRs reasonably sized (< 400 lines preferred)

## Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Docstrings for functions and classes
- 88 character line limit (Black default)

### Templates (HTML)

- Use TailwindCSS classes
- Keep templates simple and readable
- Use Django template inheritance properly

### CSS

- Use TailwindCSS utility classes
- Follow design system tokens
- Avoid inline styles

## Project Structure

```
library-ms/
├── apps/
│   ├── books/          # Book & copy management
│   ├── borrowers/      # Borrower management
│   ├── loans/          # Loan tracking & returns
│   ├── notifications/  # Settings, backup, branding
│   └── setup/         # Setup wizard & configuration
├── config/             # Django settings
├── templates/          # HTML templates
├── static/            # CSS, JS
├── media/              # Uploaded images
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Reporting Issues

Before creating an issue, please:

1. Check if the issue already exists
2. Use the issue template
3. Provide as much detail as possible:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots if applicable

## Questions?

- Open a [Discussion](https://github.com/YOUR_USERNAME/library-ms/discussions)
- Check the [documentation](https://library-ms.readthedocs.io)

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
