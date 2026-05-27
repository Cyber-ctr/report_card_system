from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Student, Subject, SchoolClass, Score, ReportCard
from ..services import current_school_settings

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    settings = current_school_settings()
    return render_template("main/index.html", settings=settings)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    settings = current_school_settings()
    if current_user.role == "admin":
        counts = {
            "students": Student.query.count(),
            "subjects": Subject.query.count(),
            "classes": SchoolClass.query.count(),
            "scores": Score.query.count(),
            "reports": ReportCard.query.count(),
        }
    elif current_user.role == "teacher":
        counts = {
            "students": Student.query.count(),
            "subjects": Subject.query.filter((Subject.teacher_id == current_user.id) | (Subject.teacher_id.is_(None))).count(),
            "classes": SchoolClass.query.count(),
            "scores": Score.query.filter_by(entered_by_id=current_user.id).count(),
            "reports": ReportCard.query.count(),
        }
    else:
        counts = {"students": 0, "subjects": 0, "classes": 0, "scores": 0, "reports": 0}

    recent_reports = ReportCard.query.order_by(ReportCard.created_at.desc()).limit(6).all()
    return render_template("main/dashboard.html", counts=counts, recent_reports=recent_reports, settings=settings)

@main_bp.route("/health")
def health():
    return {"status": "ok"}
