#!/usr/bin/env python3
"""One-shot local setup: venv, deps, migrate, seed demo data."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from venv import EnvBuilder

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
IS_WIN = os.name == "nt"
BIN = VENV / ("Scripts" if IS_WIN else "bin")
PYTHON = BIN / ("python.exe" if IS_WIN else "python")
PIP = BIN / ("pip.exe" if IS_WIN else "pip")


def run(cmd: list[str], **kwargs) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd, cwd=ROOT, **kwargs)


def main() -> int:
    if not VENV.exists():
        print("Creating virtualenv at .venv …")
        EnvBuilder(with_pip=True).create(VENV)
    else:
        print("Using existing .venv")

    run([str(PIP), "install", "--upgrade", "pip"])
    run([str(PIP), "install", "-r", "requirements.txt"])

    env_example = ROOT / ".env.example"
    env_file = ROOT / ".env"
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
        print("Created .env from .env.example")

    run([str(PYTHON), "manage.py", "migrate", "--noinput"])
    run([str(PYTHON), "manage.py", "seed_demo_data"])

    activate = BIN / ("activate" if not IS_WIN else "activate.bat")
    print()
    print("Setup complete.")
    print()
    print("Start the server:")
    if IS_WIN:
        print(r"  .\.venv\Scripts\activate")
        print(r"  python manage.py runserver")
    else:
        print(f"  source {activate.relative_to(ROOT)}")
        print("  python manage.py runserver")
    print()
    print("Then open http://127.0.0.1:8000/login/")
    print("Demo logins: owner/owner123  admin/admin123  jane/teacher123")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
