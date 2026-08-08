# Studio Hours — login details
# Copy to LOGINS.md and fill in. Do not commit LOGINS.md.

## Local (http://127.0.0.1:8000/login/)
Seeded by `python manage.py seed_demo_data` / `python setup_local.py`:

| Role | Username | Password |
|------|----------|----------|
| Owner | owner | owner123 |
| Owner | admin | admin123 |
| Teacher | jane | teacher123 |
| Teacher | mark | teacher123 |
| Teacher | ava | teacher123 |

## Production (https://soulful.fly.dev)
| Role | Username | Password |
|------|----------|----------|
| Owner | owner | your-password |
| Owner | admin | your-password |
| Teacher | … | your-password |

## Notes
- Django admin: /admin/ (owner or admin account)
- Owners can add/remove teachers and change teacher usernames/passwords on the Teachers page (`/teachers/`)
- To change passwords via CLI: python manage.py changepassword <username>
