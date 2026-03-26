#!/bin/bash
set -e

for dir in /app/data /app/staticfiles /app/media; do
    mkdir -p "${dir}"
done

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Fixing data ownership..."
chown -R appuser:appgroup /app/data /app/staticfiles /app/media 2>/dev/null || true

echo "[entrypoint] Starting gunicorn as appuser..."
exec runuser -u appuser -- /bin/sh -c "cd /app && exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application"
