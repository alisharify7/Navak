from flask import Blueprint

setting = Blueprint("setting", __name__)
from navak_setting import views
