# Remote Report Card System

A secure Flask-based report card system for secondary schools.

## Features
- Role-based authentication
- Admin management for classes, subjects, students, and users
- Teacher score entry
- Automatic grading
- Printable/PDF report cards
- Audit logging
- PostgreSQL-ready, SQLite by default

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`.

## Create the database

The app uses SQLite automatically if `DATABASE_URL` is not set. For PostgreSQL, set it in `.env`.

## Create an admin user

Use the built-in CLI command:

```bash
flask create-admin
```

## Default login

Create your own admin user with the command above.
