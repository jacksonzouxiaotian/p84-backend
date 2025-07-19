from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, NumberRange


class PhaseStatusForm(FlaskForm):
    user_id = IntegerField("User ID", validators=[
        DataRequired(),
        NumberRange(min=1, message="Invalid user ID")
    ])
    phase_number = IntegerField("Phase Number", validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message="Phase must be between 1 and 5")
    ])
    title = StringField("Title", validators=[DataRequired()])
    
    status = SelectField("Status", choices=[
        ("NotCompleted", "Not Completed"),
        ("Completed", "Completed")
    ], validators=[DataRequired()])
