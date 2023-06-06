from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, TextAreaField, SelectField, IntegerField, \
    HiddenField
from wtforms.validators import DataRequired, InputRequired, Length

import navak_config.config as config
from navak_admin.utils import get_all_education, get_all_work_position, get_all_roles
from navak_config.utils import load_work_position



class SearchInProjects(FlaskForm):

    Options = SelectField(
        choices=config.SEARCH_PROJECT_OPTION,
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    SearchBox = StringField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    submit = SubmitField()



class AddNewProject(FlaskForm):
    """
        base form model for adding new Project to app
    """
    ProjectName = StringField(
        validators=[
            DataRequired(), InputRequired(), Length(min=1, max=256)
        ]
    )

    ProjectAmount = IntegerField(
        validators=[
            DataRequired(), InputRequired(),
        ]
    )

    ProjectHandler = StringField(
        validators=[
            DataRequired(), InputRequired(), Length(min=1, max=256)
        ]
    )

    ProjectType = SelectField(
        choices=config.PROJECT_TYPE,
        validators=[
            DataRequired(), InputRequired()
        ]
    )
    ProjectStatus = SelectField(
        choices=config.PROJECT_STATUS_TYPE,
        validators=[
            DataRequired(), InputRequired(),
        ]
    )

    ProjectStartDate = StringField(
        validators=[
            DataRequired(), InputRequired(),
        ]
    )
    ProjectEndDate = StringField(
        validators=[
            DataRequired(), InputRequired(),
        ]
    )
    ProjectProducts = HiddenField()
    ProjectDescription = TextAreaField(
        validators=[
            Length(min=0, max=2048)
        ]
    )


class AddNewUserForm(FlaskForm):
    """
        this Form Uses for add new user to app
        uses in /manage-users/add
    """
    Username = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )
    Password = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=102)
        ]
    )
    Fullname = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=102)
        ]
    )
    Active = RadioField(
        choices=[("inactive", "غیرفعال"), ("active", "فعال")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    UserRole = SelectField(
        choices=get_all_roles(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )
    Submit = SubmitField()


class EditUserForm(FlaskForm):
    """
        this Form Uses for edit a user
        uses in /manage-users/edit
    """
    Username = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )

    Password = StringField(
        validators=[
        ]
    )

    Fullname = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=102)
        ]
    )
    Active = RadioField(
        choices=[("inactive", "غیرفعال"), ("active", "فعال")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    UserRole = SelectField(
        choices=get_all_roles(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )
    Submit = SubmitField()


class AddNewEmployeeForm(FlaskForm):
    """
        this form uses for adding new employee to app

    """
    username = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )

    password = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=102)
        ]
    )
    FirstName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    LastName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    FatherName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )
    BirthDay = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    MeliCode = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=32)
        ]
    )
    BirthDayLocation = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    PhoneNumber = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=11, max=11)
        ]
    )
    EmergencyPhone = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=11, max=11)
        ]
    )

    Address = TextAreaField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=256)
        ]
    )

    Education = SelectField(
        choices=get_all_education(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    StaffCode = IntegerField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    ContractType = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    StartContract = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    EndContract = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    WorkPosition = SelectField(
        choices=get_all_work_position(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    Marid = RadioField(
        choices=[("marid", "متاهل"), ("bachelor", "مجرد")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    Children = IntegerField()
    BaseSalary = IntegerField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    Active = RadioField(
        choices=[("inactive", "غیرفعال"), ("active", "فعال")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    submit = SubmitField()


class EditEmployeeForm(FlaskForm):
    """
        this form uses for editing an employee in app

    """
    username = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )

    password = StringField()
    FirstName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    LastName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    FatherName = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=6, max=64)
        ]
    )
    BirthDay = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    MeliCode = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=32)
        ]
    )
    BirthDayLocation = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    PhoneNumber = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=11, max=11)
        ]
    )
    EmergencyPhone = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=11, max=11)
        ]
    )

    Address = TextAreaField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=256)
        ]
    )

    Education = SelectField(
        choices=get_all_education(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    StaffCode = IntegerField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    ContractType = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
            Length(min=1, max=64)
        ]
    )
    StartContract = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    EndContract = StringField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    WorkPosition = SelectField(
        choices=get_all_work_position(),
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    Marid = RadioField(
        choices=[("marid", "متاهل"), ("bachelor", "مجرد")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )
    Children = IntegerField()
    BaseSalary = IntegerField(
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    Active = RadioField(
        choices=[("inactive", "غیرفعال"), ("active", "فعال")],
        validators=[
            DataRequired(),
            InputRequired(),
        ]
    )

    submit = SubmitField()


class SearchFieldForm(FlaskForm):
    """
        this form take a username for searching in db for that user or employee
    """
    username = StringField(
        validators=[
            InputRequired(),
            DataRequired()
        ]
    )

    submit = SubmitField()



