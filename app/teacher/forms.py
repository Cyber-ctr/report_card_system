from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length

class ScoreForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    term = SelectField("Term", choices=[
        ("First Term", "First Term"),
        ("Second Term", "Second Term"),
        ("Third Term", "Third Term"),
    ], validators=[DataRequired()])
    academic_year = StringField("Academic Year", validators=[DataRequired(), Length(min=4, max=20)])
    ca_score = FloatField("CA Score", validators=[DataRequired(), NumberRange(min=0, max=40)])
    exam_score = FloatField("Exam Score", validators=[DataRequired(), NumberRange(min=0, max=60)])
    teacher_comment = TextAreaField("Teacher Comment", validators=[Length(max=255)])
    submit = SubmitField("Save Score")
