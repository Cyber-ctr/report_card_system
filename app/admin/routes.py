from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from flask_login import login_required, current_user
from ..decorators import role_required
from ..extensions import db
from ..models import User, SchoolClass, Subject, Student
from ..auth.forms import UserForm
from .forms import ClassForm, SubjectForm, StudentForm
from ..services import log_action

admin_bp = Blueprint("admin", __name__)

def _safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default

@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())

@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter((User.username == form.username.data) | (User.email == form.email.data.lower().strip())).first():
            flash("Username or email already exists.", "danger")
            return render_template("admin/user_form.html", form=form, title="Create User")
        user = User(username=form.username.data.strip(), email=form.email.data.lower().strip(), role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_action(current_user.id, "create_user", "User", user.id, f"Created user {user.username}", request.remote_addr)
        flash("User created successfully.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, title="Create User")

@admin_bp.route("/classes")
@login_required
@role_required("admin")
def classes():
    return render_template("admin/classes.html", classes=SchoolClass.query.order_by(SchoolClass.name).all())

@admin_bp.route("/classes/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def class_create():
    form = ClassForm()
    if form.validate_on_submit():
        item = SchoolClass(name=form.name.data.strip())
        db.session.add(item)
        db.session.commit()
        log_action(current_user.id, "create_class", "SchoolClass", item.id, f"Created class {item.name}", request.remote_addr)
        flash("Class created successfully.", "success")
        return redirect(url_for("admin.classes"))
    return render_template("admin/simple_form.html", form=form, title="Create Class")

@admin_bp.route("/subjects")
@login_required
@role_required("admin")
def subjects():
    return render_template("admin/subjects.html", subjects=Subject.query.order_by(Subject.name).all())

@admin_bp.route("/subjects/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def subject_create():
    form = SubjectForm()
    teachers = User.query.filter_by(role="teacher").order_by(User.username).all()
    form.teacher_id.choices = [(0, "-- None --")] + [(t.id, t.username) for t in teachers]
    if form.validate_on_submit():
        item = Subject(
            name=form.name.data.strip(),
            code=form.code.data.strip(),
            teacher_id=form.teacher_id.data or None,
        )
        db.session.add(item)
        db.session.commit()
        log_action(current_user.id, "create_subject", "Subject", item.id, f"Created subject {item.name}", request.remote_addr)
        flash("Subject created successfully.", "success")
        return redirect(url_for("admin.subjects"))
    return render_template("admin/simple_form.html", form=form, title="Create Subject")

@admin_bp.route("/students")
@login_required
@role_required("admin")
def students():
    return render_template("admin/students.html", students=Student.query.order_by(Student.id.desc()).all())

@admin_bp.route("/students/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def student_create():
    form = StudentForm()
    form.class_id.choices = [(c.id, c.name) for c in SchoolClass.query.order_by(SchoolClass.name).all()]
    form.parent_user_id.choices = [(0, "-- None --")] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(role="parent").order_by(User.username).all()]
    if form.validate_on_submit():
        if Student.query.filter_by(admission_number=form.admission_number.data.strip()).first():
            flash("Admission number already exists.", "danger")
            return render_template("admin/student_form.html", form=form, title="Create Student")
        student = Student(
            admission_number=form.admission_number.data.strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            gender=form.gender.data,
            date_of_birth=form.date_of_birth.data,
            class_id=form.class_id.data,
            guardian_name=form.guardian_name.data or None,
            guardian_phone=form.guardian_phone.data or None,
            guardian_email=form.guardian_email.data or None,
            parent_user_id=form.parent_user_id.data or None,
        )
        db.session.add(student)
        db.session.commit()
        log_action(current_user.id, "create_student", "Student", student.id, f"Created student {student.first_name} {student.last_name}", request.remote_addr)
        flash("Student created successfully.", "success")
        return redirect(url_for("admin.students"))
    return render_template("admin/student_form.html", form=form, title="Create Student")
