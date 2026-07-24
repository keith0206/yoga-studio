#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Fly Machines use an IPv6 private network (6PN). Bind [::] so the proxy
# health check can reach us; with IPV6_V6ONLY=0 this also accepts IPv4.
# Do not also bind 0.0.0.0 — that dual-stack conflict exits gunicorn.
exec gunicorn --bind '[::]:8000' --workers 1 --threads 2 --timeout 60 config.wsgi:application
