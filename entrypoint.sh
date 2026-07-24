#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Fly's private network is IPv6; some proxy paths also use IPv4.
# Bind both so health checks and public traffic can reach the app.
exec gunicorn \
  --bind '0.0.0.0:8000' \
  --bind '[::]:8000' \
  --workers 1 \
  --threads 2 \
  --timeout 60 \
  config.wsgi:application
