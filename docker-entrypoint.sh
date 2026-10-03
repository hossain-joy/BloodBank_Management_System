#!/bin/sh
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn bloodbank.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120
