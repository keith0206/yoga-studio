#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Fly proxy health checks probe 0.0.0.0:8000 — bind IPv4 explicitly.
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 60 config.wsgi:application
