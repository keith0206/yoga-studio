# Studio Hours — login details
# Copy to LOGINS.md and fill in. Do not commit LOGINS.md.

## Local (http://127.0.0.1:8000/login/)
| Role | Username | Password |
|------|----------|----------|
| Owner | owner | your-password |
| Owner | admin | your-password |
| Teacher | jane | your-password |
| Teacher | mark | your-password |
| Teacher | ava | your-password |

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
