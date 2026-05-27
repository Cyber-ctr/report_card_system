from datetime import datetime
from uuid import uuid4

from flask_login import UserMixin

from .extensions import db, bcrypt, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="teacher")
    is_active_account = db.Column(db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except Exception:
            return False

    @property
    def is_active(self):
        return self.is_active_account

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None

class SchoolClass(db.Model):
    __tablename__ = "school_classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    stream = db.Column(db.String(40), nullable=True)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    students = db.relationship("Student", back_populates="school_class", cascade="all, delete-orphan")
    subjects = db.relationship("Subject", back_populates="school_class")

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    coefficient = db.Column(db.Integer, default=1, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id"), nullable=True)

    teacher = db.relationship("User", foreign_keys=[teacher_id])
    school_class = db.relationship("SchoolClass", back_populates="subjects")
    scores = db.relationship("Score", back_populates="subject", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("name", "class_id", name="uq_subject_name_class"),)

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey("school_classes.id"), nullable=False)

    guardian_name = db.Column(db.String(120), nullable=True)
    guardian_phone = db.Column(db.String(50), nullable=True)
    guardian_email = db.Column(db.String(120), nullable=True)

    parent_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    school_class = db.relationship("SchoolClass", back_populates="students")
    parent_user = db.relationship("User", foreign_keys=[parent_user_id])
    student_user = db.relationship("User", foreign_keys=[user_id])
    scores = db.relationship("Score", back_populates="student", cascade="all, delete-orphan")
    report_cards = db.relationship("ReportCard", back_populates="student", cascade="all, delete-orphan")

class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    entered_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    ca_score = db.Column(db.Float, nullable=False, default=0)
    exam_score = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False, default=0)
    grade = db.Column(db.String(5), nullable=False, default="F")
    remark = db.Column(db.String(255), nullable=True)
    teacher_comment = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="scores")
    subject = db.relationship("Subject", back_populates="scores")
    entered_by = db.relationship("User", foreign_keys=[entered_by_id])

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", "term", "academic_year", name="uq_score_student_subject_term_year"),
    )

class ReportCard(db.Model):
    __tablename__ = "report_cards"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="draft", nullable=False)
    verification_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid4().hex)
    overall_comment = db.Column(db.String(255), nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    published_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="report_cards")
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])
    published_by = db.relationship("User", foreign_keys=[published_by_id])

    __table_args__ = (
        db.UniqueConstraint("student_id", "term", "academic_year", name="uq_report_student_term_year"),
    )

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(80), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User")

class SchoolSettings(db.Model):
    __tablename__ = "school_settings"

    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(160), nullable=False, default="Secondary School")
    motto = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    academic_year = db.Column(db.String(20), nullable=False, default="2026/2027")
    current_term = db.Column(db.String(50), nullable=False, default="First Term")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
