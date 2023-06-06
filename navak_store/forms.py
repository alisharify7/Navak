from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, FloatField, SelectField, RadioField, \
    HiddenField
from wtforms.validators import InputRequired, DataRequired, Length

import navak_config.config as config


class AddNewProductForm(FlaskForm):
    """
        base from for adding new product to db
    """

    ProductName = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=256, message="طول نام محصول باید بین 1 تا 256 کاراکتر باشد")
    ])
    ProductPartNumber = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=256, message="طول پارت نامبر محصول باید بین 1 تا 256 کاراکتر باشد")
    ])
    ProductStoreId = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=256, message="طول شماره انبار محصول باید بین 1 تا 256 کاراکتر باشد")
    ])
    ProductDescription = TextAreaField(validators=[
        Length(min=0, max=2048, message="حداکثر طول توضیحات محصول 2048 کاراکتر و حداقل 1 است")
    ])
    ProductType = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=128, message="طول نوع محصول باید بین 1 تا 128 کاراکتر باشد")
    ])
    ProductManufacture = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=256, message="طول کارخانه سازنده محصول باید بین 1 تا 256 کاراکتر باشد")
    ])
    ProductPrice = FloatField(validators=[
        InputRequired(),
        DataRequired(),
    ])
    ProductBuyFrom = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=128, message="طول شرکت خریداری شده محصول باید بین 1 تا 128 کاراکتر باشد")
    ])
    ProductQuantity = IntegerField(validators=[
        InputRequired(),
        DataRequired(),
    ])
    ProductEnterDate = StringField(validators=[
        InputRequired(),
        DataRequired(),
    ])
    ProductPackage = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=128, message="طول پکیج محصول باید بین 1 تا 128 کاراکتر باشد")
    ])
    ProductBringPerson = StringField(validators=[
        InputRequired(),
        DataRequired(),
        Length(min=1, max=128, message="طول نام شخص آورده محصول باید بین 1 تا 128 کاراکتر باشد")
    ])

    submit = SubmitField()


class SearchProductForm(FlaskForm):
    """
        this form is uses for see product only admin type his filter and view only return simular product
    """
    SearchOptions = SelectField(
        choices=config.SEARCHOPTIONFORM,
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    ResultOption = RadioField(
        choices=[
            ("first", "اولین"),
            ("all", "تمام")
        ],
        validators=[
            DataRequired(),
            InputRequired()
        ]

    )

    SearchBox = StringField(
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    submit = SubmitField()



class SearchEditProductForm(FlaskForm):
    """
        this form is uses for search in product and if found any thing let admin edit it
        uses in edit product view
    """
    SearchOptions = SelectField(
        choices=config.SEARCHOPTIONFORM,
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    SearchBox = StringField(
        validators=[
            DataRequired(),
            InputRequired()
        ]
    )

    submit = SubmitField()


class SearchInProjectProduct(FlaskForm):
    """
        this form uses when store staff want search in projects for exit products
    """
    ProjectId = IntegerField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    submit = SubmitField()



class ProductExitProject(FlaskForm):
    """
        this for uses  for exit product's from store thats belong to a project
    """
    Products = HiddenField()
    ProjectKey = HiddenField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    PersonName = StringField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    Description = TextAreaField(
        validators=[]
    )
    submit = SubmitField()


class ProductExitPerson(FlaskForm):
    """
        this for uses for exit product's from store By anyOne
    """
    Products = HiddenField()

    PersonName = StringField(
        validators=[
            DataRequired(), InputRequired()
        ]
    )

    Description = TextAreaField(
        validators=[]
    )
    submit = SubmitField()
