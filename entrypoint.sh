#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Bind IPv6 ([::]) so Fly's proxy/health checks can reach the app (they use IPv6).
exec gunicorn --bind [::]:8000 --workers 1 --threads 2 config.wsgi:application
