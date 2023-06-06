from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, FileField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length

import navak_config.config as config


class SendMailForm(FlaskForm):
    """
        this form uses for send message between users
    """
    MailTitle = StringField(
        validators=[InputRequired(), DataRequired(), Length(min=1, max=128)]
    )

    MailCaption = TextAreaField(
        validators=[InputRequired(), DataRequired(), Length(min=1, max=4096)]
    )

    MailTarget = StringField(
        validators=[InputRequired(), DataRequired()]
    )

    MailAttach = FileField(
        validators=[]
    )

    submit = SubmitField()


class SearchMailForm(FlaskForm):
    """
        this form uses when users want to search in his mailbox messages
    """
    SearchOption = SelectField(
        choices=config.SEARCH_OPTION_MAIL_FORM,
        validators=[InputRequired(), DataRequired()]
    )

    SearchTarget = SelectField(
        choices=[("receiver", "دریافت کرده ام"), ("sender", "فرستاده ام")],
        validators=[InputRequired(), DataRequired()]
    )

    SearchBox = StringField(
        validators=[InputRequired(), DataRequired()]
    )

    submit = SubmitField()
