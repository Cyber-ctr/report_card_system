from flask import Blueprint, abort, render_template, make_response
from flask_login import login_required, current_user
from ..decorators import role_required
from ..models import Student, Score
from ..services import grade_from_total
try:
    from weasyprint import HTML
except Exception:
    HTML = None

reports_bp = Blueprint("reports", __name__)

def _scores_for(student_id, term=None, academic_year=None):
    q = Score.query.filter_by(student_id=student_id)
    if term:
        q = q.filter_by(term=term)
    if academic_year:
        q = q.filter_by(academic_year=academic_year)
    return q.order_by(Score.subject_id).all()

@reports_bp.route("/student/<int:student_id>")
@login_required
def report_card(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.role == "parent" and student.parent_user_id != current_user.id:
        abort(403)
    if current_user.role not in ("admin", "teacher", "parent", "student"):
        abort(403)

    term = "First Term"
    academic_year = "2026/2027"
    scores = _scores_for(student_id, term=term, academic_year=academic_year)
    total = sum(s.total for s in scores)
    average = round(total / len(scores), 2) if scores else 0
    context = {
        "student": student,
        "scores": scores,
        "total": total,
        "average": average,
        "term": term,
        "academic_year": academic_year,
    }
    return render_template("reports/report_card.html", **context)

@reports_bp.route("/student/<int:student_id>/pdf")
@login_required
def report_card_pdf(student_id):
    student = Student.query.get_or_404(student_id)
    if current_user.role == "parent" and student.parent_user_id != current_user.id:
        abort(403)
    term = "First Term"
    academic_year = "2026/2027"
    scores = _scores_for(student_id, term=term, academic_year=academic_year)
    total = sum(s.total for s in scores)
    average = round(total / len(scores), 2) if scores else 0
    html = render_template("reports/report_card_pdf.html", student=student, scores=scores, total=total, average=average, term=term, academic_year=academic_year)
    if HTML is None:
        return html
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="report_card_{student.admission_number}.pdf"'
    return response
