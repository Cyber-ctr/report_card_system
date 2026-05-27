from datetime import datetime

from flask import Blueprint, abort, render_template, make_response, current_app, request
from flask_login import login_required, current_user

try:
    from weasyprint import HTML
except Exception:
    HTML = None

from ..extensions import db
from ..models import Student, ReportCard
from ..services import report_context, log_action, current_school_settings

reports_bp = Blueprint("reports", __name__)

def _can_access(student, report=None):
    if current_user.role == "admin":
        return True
    if current_user.role == "teacher":
        return True
    if current_user.role == "parent":
        return student.parent_user_id == current_user.id and (report is None or report.status == "published")
    if current_user.role == "student":
        return student.user_id == current_user.id and (report is None or report.status == "published")
    return False

@reports_bp.route("/student/<int:student_id>")
@login_required
def report_card(student_id):
    student = Student.query.get_or_404(student_id)
    settings = current_school_settings()
    report = ReportCard.query.filter_by(student_id=student.id, term=settings.current_term, academic_year=settings.academic_year).first()
    if not _can_access(student, report):
        abort(403)

    if not report:
        report = ReportCard(student_id=student.id, term=settings.current_term, academic_year=settings.academic_year)
        db.session.add(report)
        db.session.commit()

    context = report_context(student, settings.current_term, settings.academic_year)
    return render_template("reports/report_card.html", report=report, settings=settings, **context, title="Report Card")

@reports_bp.route("/student/<int:student_id>/pdf")
@login_required
def report_card_pdf(student_id):
    student = Student.query.get_or_404(student_id)
    settings = current_school_settings()
    report = ReportCard.query.filter_by(student_id=student.id, term=settings.current_term, academic_year=settings.academic_year).first()
    if not _can_access(student, report):
        abort(403)

    if not report:
        report = ReportCard(student_id=student.id, term=settings.current_term, academic_year=settings.academic_year)
        db.session.add(report)
        db.session.commit()

    context = report_context(student, settings.current_term, settings.academic_year)
    html = render_template("reports/report_card_pdf.html", report=report, settings=settings, **context, title="Report Card")
    if HTML is None:
        response = make_response(html)
        response.headers["Content-Type"] = "text/html"
        return response

    pdf = HTML(string=html, base_url=current_app.root_path).write_pdf()
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="report_card_{student.admission_number}.pdf"'
    return response

@reports_bp.route("/verify/<token>")
def verify_report(token):
    report = ReportCard.query.filter_by(verification_token=token).first_or_404()
    student = report.student
    settings = current_school_settings()
    context = report_context(student, report.term, report.academic_year)
    return render_template("reports/verify.html", report=report, settings=settings, **context, title="Verification")

@reports_bp.route("/approve/<int:report_id>", methods=["POST"])
@login_required
def approve_report(report_id):
    report = ReportCard.query.get_or_404(report_id)
    if current_user.role not in ("admin", "teacher"):
        abort(403)
    if report.status == "draft":
        report.status = "approved"
        report.approved_by_id = current_user.id
        report.approved_at = datetime.utcnow()
        db.session.commit()
        log_action(current_user.id, "approve_report", "ReportCard", report.id, "Approved report card", request.remote_addr)
    return {"status": report.status, "token": report.verification_token}

@reports_bp.route("/publish/<int:report_id>", methods=["POST"])
@login_required
def publish_report(report_id):
    report = ReportCard.query.get_or_404(report_id)
    if current_user.role not in ("admin", "teacher"):
        abort(403)
    if report.status != "published":
        report.status = "published"
        report.published_by_id = current_user.id
        report.published_at = datetime.utcnow()
        db.session.commit()
        log_action(current_user.id, "publish_report", "ReportCard", report.id, "Published report card", request.remote_addr)
    return {"status": report.status, "token": report.verification_token}
