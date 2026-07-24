#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
mkdir -p /data
python manage.py migrate --noinput

# Fly Proxy and service checks connect to the configured internal IPv4 port.
exec gunicorn \
    --workers 1 \
    --threads 2 \
    --timeout 60 \
    --bind "0.0.0.0:${PORT:-8000}" \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application
