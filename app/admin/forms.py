from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange

class ClassForm(FlaskForm):
    name = StringField("Class Name", validators=[DataRequired(), Length(min=1, max=80)])
    stream = StringField("Stream", validators=[Optional(), Length(max=40)])
    order_index = IntegerField("Order", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Save")

class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired(), Length(min=1, max=120)])
    code = StringField("Code", validators=[DataRequired(), Length(min=1, max=20)])
    coefficient = IntegerField("Coefficient", validators=[DataRequired(), NumberRange(min=1, max=10)])
    teacher_id = SelectField("Teacher", coerce=int, validators=[Optional()])
    class_id = SelectField("Class", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class StudentForm(FlaskForm):
    admission_number = StringField("Admission Number", validators=[DataRequired(), Length(min=1, max=50)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=1, max=80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=80)])
    gender = SelectField("Gender", choices=[("Male", "Male"), ("Female", "Female")], validators=[DataRequired()])
    date_of_birth = DateField("Date of Birth", validators=[Optional()], format="%Y-%m-%d")
    class_id = SelectField("Class", coerce=int, validators=[DataRequired()])
    guardian_name = StringField("Guardian Name", validators=[Optional(), Length(max=120)])
    guardian_phone = StringField("Guardian Phone", validators=[Optional(), Length(max=50)])
    guardian_email = StringField("Guardian Email", validators=[Optional(), Email()])
    parent_user_id = SelectField("Parent Account", coerce=int, validators=[Optional()])
    user_id = SelectField("Student Account", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")

class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired(), Length(min=8)])
    role = SelectField("Role", choices=[
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
        ("student", "Student"),
    ], validators=[DataRequired()])
    is_active_account = BooleanField("Active", default=True)
    submit = SubmitField("Save")

class SchoolSettingsForm(FlaskForm):
    school_name = StringField("School Name", validators=[DataRequired(), Length(min=3, max=160)])
    motto = StringField("Motto", validators=[Optional(), Length(max=255)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    contact_email = StringField("Contact Email", validators=[Optional(), Email()])
    contact_phone = StringField("Contact Phone", validators=[Optional(), Length(max=50)])
    academic_year = StringField("Academic Year", validators=[DataRequired(), Length(min=4, max=20)])
    current_term = SelectField("Current Term", choices=[
        ("First Term", "First Term"),
        ("Second Term", "Second Term"),
        ("Third Term", "Third Term"),
    ], validators=[DataRequired()])
    submit = SubmitField("Save")
