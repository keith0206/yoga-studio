# Soulful — yoga studio hours

Django app for studio schedules, teachers, and attendance. Production: [soulful.fly.dev](https://soulful.fly.dev).

## Run locally

Needs **Python 3.11+**.

```bash
git clone https://github.com/keith0206/yoga-studio.git
cd yoga-studio
python setup_local.py
```

Then start the server:

**macOS / Linux**
```bash
source .venv/bin/activate
python manage.py runserver
```

**Windows (PowerShell)**
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Open [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/).

### Demo logins (from seed)

| Role | Username | Password |
|------|----------|----------|
| Owner | `owner` | `owner123` |
| Owner | `admin` | `admin123` |
| Teacher | `jane` / `mark` / `ava` | `teacher123` |

Re-seed anytime: `python manage.py seed_demo_data`

### Manual setup (if you skip the script)

```bash
python -m venv .venv
# activate .venv (see above)
pip install -r requirements.txt
cp .env.example .env   # optional
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Local DB defaults to SQLite (`db.sqlite3`). No Postgres required.
