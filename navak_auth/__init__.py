from flask import Blueprint


auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

import navak_auth.views
