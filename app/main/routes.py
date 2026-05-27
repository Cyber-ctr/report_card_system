from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Student, Subject, SchoolClass, Score
from ..decorators import role_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("main/index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        counts = {
            "students": Student.query.count(),
            "subjects": Subject.query.count(),
            "classes": SchoolClass.query.count(),
            "scores": Score.query.count(),
        }
    elif current_user.role == "teacher":
        counts = {
            "students": Student.query.count(),
            "subjects": Subject.query.filter_by(teacher_id=current_user.id).count(),
            "classes": SchoolClass.query.count(),
            "scores": Score.query.filter_by(entered_by_id=current_user.id).count(),
        }
    else:
        counts = {"students": 0, "subjects": 0, "classes": 0, "scores": 0}
    return render_template("main/dashboard.html", counts=counts)
