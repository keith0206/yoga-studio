#!/bin/sh
set -e

# Volume-backed SQLite: migrate on the machine that has /data mounted.
# (Fly release_command machines do not receive volume mounts.)
python manage.py migrate --noinput

# Dual-stack listen via inheritable FDs (see bind_and_run.py).
exec python /app/bind_and_run.py
