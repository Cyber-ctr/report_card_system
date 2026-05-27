from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from ..decorators import role_required
from ..extensions import db
from ..models import Student, Subject, Score
from ..services import grade_from_total, remark_from_grade, log_action
from .forms import ScoreForm

teacher_bp = Blueprint("teacher", __name__)

@teacher_bp.route("/scores", methods=["GET", "POST"])
@login_required
@role_required("teacher", "admin")
def scores():
    form = ScoreForm()
    students = Student.query.order_by(Student.first_name).all()
    subjects_query = Subject.query.order_by(Subject.name).all()
    form.student_id.choices = [(s.id, f"{s.admission_number} - {s.first_name} {s.last_name}") for s in students]
    if current_user.role == "teacher":
        subjects_query = Subject.query.filter((Subject.teacher_id == current_user.id) | (Subject.teacher_id.is_(None))).order_by(Subject.name).all()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects_query]

    if form.validate_on_submit():
        score = Score.query.filter_by(
            student_id=form.student_id.data,
            subject_id=form.subject_id.data,
            term=form.term.data,
            academic_year=form.academic_year.data.strip(),
        ).first()

        total = float(form.ca_score.data or 0) + float(form.exam_score.data or 0)
        grade = grade_from_total(total)
        remark = remark_from_grade(grade)

        if score:
            score.ca_score = form.ca_score.data
            score.exam_score = form.exam_score.data
            score.total = total
            score.grade = grade
            score.remark = remark
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
            )
            db.session.add(score)

        db.session.commit()
        log_action(current_user.id, "save_score", "Score", score.id, f"Saved score for student {score.student_id}", request.remote_addr)
        flash("Score saved successfully.", "success")
        return redirect(url_for("teacher.scores"))

    records = Score.query.order_by(Score.created_at.desc()).limit(200).all()
    return render_template("teacher/scores.html", form=form, records=records)
