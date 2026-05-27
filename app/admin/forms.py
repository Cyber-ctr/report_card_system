from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, FloatField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange

class ClassForm(FlaskForm):
    name = StringField("Class Name", validators=[DataRequired(), Length(min=1, max=80)])
    submit = SubmitField("Save")

class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired(), Length(min=1, max=120)])
    code = StringField("Code", validators=[DataRequired(), Length(min=1, max=20)])
    teacher_id = SelectField("Teacher", coerce=int, validators=[Optional()])
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
    parent_user_id = SelectField("Parent User", coerce=int, validators=[Optional()])
    submit = SubmitField("Save")
