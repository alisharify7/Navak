from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, InputRequired


class SearchInProjects(FlaskForm):
    """
        this form uses for searchin in project for a specific project
    """
    SearchBox = IntegerField(
        validators=[
            InputRequired(), DataRequired()
        ]
    )

    submit = SubmitField()


class AddCommentProject(FlaskForm):
    """
        this form uses for adding new comment about project's by engineers
    """
    ProjectKey = HiddenField()

    Comment = TextAreaField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    submit = SubmitField()
