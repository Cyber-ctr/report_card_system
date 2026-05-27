# ScholaTrack

ScholaTrack — Secure Academic Reporting Platform for secondary schools.

## Features
- Secure login with password hashing
- Role-based access control
- Admin management for users, classes, subjects, and students
- Teacher score entry with automatic grading
- Report card preview, approval, publishing, PDF export, and token verification
- Audit logging
- Security headers and rate limiting
- SQLite by default, PostgreSQL-ready for production

## Quick start
```bash
python -m venv .venv
pip install -r requirements.txt
copy .env.example .env
python run.py
```

## Initialize the database
For local development, the app can auto-create tables on startup when `AUTO_CREATE_DB=true`.

```bash
flask seed-admin
```

## Default admin
Use `flask seed-admin` to create one.
