from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from ..decorators import role_required
from ..extensions import db
from ..models import User, SchoolClass, Subject, Student, ReportCard
from ..services import log_action, current_school_settings
from .forms import ClassForm, SubjectForm, StudentForm, UserForm, SchoolSettingsForm

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all(), title="Users")

@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter((User.username == form.username.data.strip()) | (User.email == form.email.data.strip().lower())).first():
            flash("Username or email already exists.", "danger")
            return render_template("admin/user_form.html", form=form, title="Create User")
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role=form.role.data,
            is_active_account=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Could not create user. Please check for duplicate values.", "danger")
            return render_template("admin/user_form.html", form=form, title="Create User")
        log_action(current_user.id, "create_user", "User", user.id, f"Created user {user.username}", request.remote_addr)
        flash("User created successfully.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, title="Create User")

@admin_bp.route("/classes")
@login_required
@role_required("admin")
def classes():
    items = SchoolClass.query.order_by(SchoolClass.order_index.asc(), SchoolClass.name.asc()).all()
    return render_template("admin/classes.html", classes=items, title="Classes")

@admin_bp.route("/classes/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def class_create():
    form = ClassForm()
    if form.validate_on_submit():
        item = SchoolClass(
            name=form.name.data.strip(),
            stream=form.stream.data.strip() if form.stream.data else None,
            order_index=form.order_index.data or 0,
        )
        db.session.add(item)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Class already exists.", "danger")
            return render_template("admin/class_form.html", form=form, title="Create Class")
        log_action(current_user.id, "create_class", "SchoolClass", item.id, f"Created class {item.name}", request.remote_addr)
        flash("Class created successfully.", "success")
        return redirect(url_for("admin.classes"))
    return render_template("admin/class_form.html", form=form, title="Create Class")

@admin_bp.route("/subjects")
@login_required
@role_required("admin")
def subjects():
    items = Subject.query.order_by(Subject.name.asc()).all()
    return render_template("admin/subjects.html", subjects=items, title="Subjects")

@admin_bp.route("/subjects/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def subject_create():
    form = SubjectForm()
    teachers = User.query.filter_by(role="teacher").order_by(User.username).all()
    classes = SchoolClass.query.order_by(SchoolClass.order_index.asc(), SchoolClass.name.asc()).all()
    form.teacher_id.choices = [(0, "-- None --")] + [(t.id, t.username) for t in teachers]
    form.class_id.choices = [(0, "-- None --")] + [(c.id, c.name) for c in classes]
    if form.validate_on_submit():
        item = Subject(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            coefficient=form.coefficient.data,
            teacher_id=form.teacher_id.data or None,
            class_id=form.class_id.data or None,
        )
        db.session.add(item)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Subject already exists or code is duplicated.", "danger")
            return render_template("admin/subject_form.html", form=form, title="Create Subject")
        log_action(current_user.id, "create_subject", "Subject", item.id, f"Created subject {item.name}", request.remote_addr)
        flash("Subject created successfully.", "success")
        return redirect(url_for("admin.subjects"))
    return render_template("admin/subject_form.html", form=form, title="Create Subject")

@admin_bp.route("/students")
@login_required
@role_required("admin")
def students():
    return render_template("admin/students.html", students=Student.query.order_by(Student.created_at.desc()).all(), title="Students")

@admin_bp.route("/students/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def student_create():
    form = StudentForm()
    form.class_id.choices = [(c.id, c.name) for c in SchoolClass.query.order_by(SchoolClass.order_index.asc(), SchoolClass.name.asc()).all()]
    form.parent_user_id.choices = [(0, "-- None --")] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(role="parent").order_by(User.username).all()]
    form.user_id.choices = [(0, "-- None --")] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(role="student").order_by(User.username).all()]
    if form.validate_on_submit():
        student = Student(
            admission_number=form.admission_number.data.strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            gender=form.gender.data,
            date_of_birth=form.date_of_birth.data,
            class_id=form.class_id.data,
            guardian_name=form.guardian_name.data.strip() if form.guardian_name.data else None,
            guardian_phone=form.guardian_phone.data.strip() if form.guardian_phone.data else None,
            guardian_email=form.guardian_email.data.strip().lower() if form.guardian_email.data else None,
            parent_user_id=form.parent_user_id.data or None,
            user_id=form.user_id.data or None,
        )
        db.session.add(student)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Admission number already exists or account links are invalid.", "danger")
            return render_template("admin/student_form.html", form=form, title="Create Student")
        log_action(current_user.id, "create_student", "Student", student.id, f"Created student {student.first_name} {student.last_name}", request.remote_addr)
        flash("Student created successfully.", "success")
        return redirect(url_for("admin.students"))
    return render_template("admin/student_form.html", form=form, title="Create Student")

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("admin")
def settings():
    settings = current_school_settings()
    form = SchoolSettingsForm(obj=settings)
    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.commit()
        log_action(current_user.id, "update_settings", "SchoolSettings", settings.id, "Updated school settings", request.remote_addr)
        flash("School settings updated.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", form=form, settings=settings, title="Settings")

@admin_bp.route("/reports")
@login_required
@role_required("admin")
def reports():
    return render_template("admin/reports.html", reports=ReportCard.query.order_by(ReportCard.created_at.desc()).all(), title="Reports")
