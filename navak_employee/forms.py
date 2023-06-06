from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length


class VacationRequest(FlaskForm):
    RequestTitle = StringField(
        validators=[DataRequired(), InputRequired(), Length(min=1, max=64)]
    )
    RequestBody = TextAreaField(
        validators=[DataRequired(), InputRequired(), Length(min=0, max=256)]
    )

    RequestTargetDate = StringField(
        validators=[DataRequired(), InputRequired()]
    )

    RequestTarget = SelectField(
        choices=[(f"{i}h", f"{i} ساعت") for i in range(1, 5)] + [(f"{i}d", f"{i} روز") for i in range(1, 5)]
    )

    submit = SubmitField()

class WorkReport(FlaskForm):
    """
        Html Form For Write Work Report For each Employee
    """
    ReportWorkBody = TextAreaField(
        validators=[DataRequired(), InputRequired(), Length(min=0, max=1024)]
    )

    submit = SubmitField()
