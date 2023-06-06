from flask import Blueprint


engineer = Blueprint("engineer", __name__, static_folder="static", template_folder="templates")
import navak_engineer.views