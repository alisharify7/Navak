from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, DataRequired


class RegisterGuestTraffic(FlaskForm):
    """
        this form uses for register guest people traffic in system
    """
    title = StringField(
        validators=[InputRequired(), DataRequired()]
    )

    description = TextAreaField(
        validators=[InputRequired(), DataRequired()]
    )

    submit = SubmitField()