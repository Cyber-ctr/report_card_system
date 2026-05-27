from datetime import datetime
from flask_login import UserMixin
from .extensions import db, bcrypt, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="teacher")
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_account

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    students = db.relationship("Student", backref="school_class", lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    teacher = db.relationship("User", foreign_keys=[teacher_id])

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey("school_class.id"), nullable=False)
    guardian_name = db.Column(db.String(120), nullable=True)
    guardian_phone = db.Column(db.String(50), nullable=True)
    guardian_email = db.Column(db.String(120), nullable=True)
    parent_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    parent_user = db.relationship("User", foreign_keys=[parent_user_id])

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    entered_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    student = db.relationship("Student", backref="scores")
    subject = db.relationship("Subject", backref="scores")
    entered_by = db.relationship("User", foreign_keys=[entered_by_id])
    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    ca_score = db.Column(db.Float, nullable=False, default=0)
    exam_score = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False, default=0)
    grade = db.Column(db.String(5), nullable=False, default="F")
    remark = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User")
    action = db.Column(db.String(255), nullable=False)
    entity_type = db.Column(db.String(80), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
