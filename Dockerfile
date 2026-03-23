FROM python:alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ALLOWED_HOSTS=*

ENV CSRF_TRUSTED_ORIGINS=http://localhost,http://localhost:8000

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libpq-dev \
    postgresql-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data && python manage.py migrate

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
