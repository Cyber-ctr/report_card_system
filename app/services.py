from datetime import datetime
from functools import wraps

from flask import abort, current_app, request
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import AuditLog, ReportCard, SchoolSettings, Score, Student

TERMS = [("First Term", "First Term"), ("Second Term", "Second Term"), ("Third Term", "Third Term")]

def calculate_grade(total):
    if total >= 80:
        return "A"
    if total >= 70:
        return "B"
    if total >= 60:
        return "C"
    if total >= 50:
        return "D"
    return "F"

def remark_from_grade(grade):
    return {
        "A": "Excellent",
        "B": "Very Good",
        "C": "Good",
        "D": "Pass",
        "F": "Needs Improvement",
    }.get(grade, "")

def log_action(user_id, action, entity_type=None, entity_id=None, description=None, ip_address=None):
    try:
        db.session.add(AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

def safe_commit():
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def current_school_settings():
    settings = SchoolSettings.query.first()
    if not settings:
        settings = SchoolSettings()
        db.session.add(settings)
        db.session.commit()
    return settings

def report_context(student, term, academic_year):
    scores = Score.query.filter_by(student_id=student.id, term=term, academic_year=academic_year).order_by(Score.subject_id).all()
    total = round(sum(s.total for s in scores), 2)
    coefficient_sum = sum((s.subject.coefficient or 1) for s in scores) or 1
    weighted_total = sum((s.total * (s.subject.coefficient or 1)) for s in scores)
    average = round(weighted_total / coefficient_sum, 2) if scores else 0
    grade = calculate_grade(average)
    return {
        "student": student,
        "scores": scores,
        "total": total,
        "average": average,
        "term": term,
        "academic_year": academic_year,
        "grade": grade,
        "remark": remark_from_grade(grade),
    }

def ensure_report_card(student, term, academic_year):
    report = ReportCard.query.filter_by(student_id=student.id, term=term, academic_year=academic_year).first()
    if not report:
        report = ReportCard(student_id=student.id, term=term, academic_year=academic_year)
        db.session.add(report)
        db.session.commit()
    return report

def configure_security_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' https:; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "connect-src 'self';"
        )
        return response

def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db():
        from .models import User, SchoolClass, Subject, Student, Score, ReportCard, AuditLog, SchoolSettings
        with app.app_context():
            db.create_all()
            if not SchoolSettings.query.first():
                db.session.add(SchoolSettings())
                db.session.commit()
        print("Database initialized.")

    @app.cli.command("seed-admin")
    def seed_admin():
        from getpass import getpass
        from .models import User
        username = input("Username [admin]: ").strip() or "admin"
        email = input("Email [admin@school.com]: ").strip() or "admin@school.com"
        password = getpass("Password [Admin123!]: ").strip() or "Admin123!"
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("Admin user already exists.")
            return
        user = User(username=username, email=email, role="admin", is_active_account=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("Admin user created successfully.")

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
