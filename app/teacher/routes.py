from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from ..decorators import role_required
from ..extensions import db
from ..models import Student, Subject, Score, SchoolClass, ReportCard
from ..services import calculate_grade, remark_from_grade, log_action, current_school_settings, ensure_report_card
from .forms import ScoreForm

teacher_bp = Blueprint("teacher", __name__)

def _teacher_subjects():
    q = Subject.query.order_by(Subject.name.asc())
    if current_user.role == "teacher":
        q = q.filter((Subject.teacher_id == current_user.id) | (Subject.teacher_id.is_(None)))
    return q.all()

def _teacher_students():
    q = Student.query.filter_by(is_active=True)
    if current_user.role == "teacher":
        assigned_classes = [s.class_id for s in _teacher_subjects() if s.class_id]
        if assigned_classes:
            q = q.filter(Student.class_id.in_(assigned_classes))
    return q.order_by(Student.first_name.asc(), Student.last_name.asc()).all()

def _records():
    q = Score.query.order_by(Score.updated_at.desc())
    if current_user.role == "teacher":
        q = q.filter_by(entered_by_id=current_user.id)
    return q.limit(100).all()

@teacher_bp.route("/scores", methods=["GET", "POST"])
@login_required
@role_required("teacher", "admin")
def scores():
    form = ScoreForm()
    students = _teacher_students()
    subjects = _teacher_subjects()

    form.student_id.choices = [(s.id, f"{s.admission_number} - {s.first_name} {s.last_name}") for s in students]
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects]

    settings = current_school_settings()
    class_filter = request.args.get("class_id", type=int)
    if class_filter:
        students = [s for s in students if s.class_id == class_filter]
    if not form.academic_year.data:
        form.academic_year.data = settings.academic_year
    if not form.term.data:
        form.term.data = settings.current_term

    if form.validate_on_submit():
        score = Score.query.filter_by(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            term=form.term.data,
            academic_year=form.academic_year.data.strip(),
        ).first()

        total = round((form.ca_score.data or 0) + (form.exam_score.data or 0), 2)
        grade = calculate_grade(total)
        remark = remark_from_grade(grade)

        if score:
            score.ca_score = form.ca_score.data
            score.exam_score = form.exam_score.data
            score.total = total
            score.grade = grade
            score.remark = remark
            score.teacher_comment = form.teacher_comment.data
            action = "update_score"
        else:
            score = Score(
                student_id=form.student_id.data,
                subject_id=form.subject_id.data,
                entered_by_id=current_user.id,
                term=form.term.data,
                academic_year=form.academic_year.data.strip(),
                ca_score=form.ca_score.data,
                exam_score=form.exam_score.data,
                total=total,
                grade=grade,
                remark=remark,
                teacher_comment=form.teacher_comment.data,
            )
            db.session.add(score)
            action = "create_score"

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Unable to save score. Please verify the selected student and subject.", "danger")
            return render_template("teacher/scores.html", form=form, records=_records(), classes=SchoolClass.query.order_by(SchoolClass.order_index.asc(), SchoolClass.name.asc()).all(), class_filter=class_filter, term_filter=form.term.data, year_filter=form.academic_year.data)

        log_action(current_user.id, action, "Score", score.id, f"Score saved for student {score.student_id}", request.remote_addr)
        ensure_report_card(score.student, score.term, score.academic_year)
        flash("Score saved successfully.", "success")
        return redirect(url_for("teacher.scores", class_id=class_filter or "", term=form.term.data, academic_year=form.academic_year.data))

    return render_template(
        "teacher/scores.html",
        form=form,
        records=_records(),
        classes=SchoolClass.query.order_by(SchoolClass.order_index.asc(), SchoolClass.name.asc()).all(),
        class_filter=class_filter,
        term_filter=form.term.data or settings.current_term,
        year_filter=form.academic_year.data or settings.academic_year,
        title="Scores",
    )

@teacher_bp.route("/reports")
@login_required
@role_required("teacher", "admin")
def reports():
    return render_template("teacher/reports.html", reports=ReportCard.query.order_by(ReportCard.created_at.desc()).all(), title="Reports")
