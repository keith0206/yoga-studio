#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Fly's private network is IPv6. Dual-bind (0.0.0.0 + [::]) fails with
# "Address already in use" on this image; [::] alone is the correct bind.
exec gunicorn --bind '[::]:8000' --workers 1 --threads 2 --timeout 60 config.wsgi:application
