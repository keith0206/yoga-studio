#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 config.wsgi:application
