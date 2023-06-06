from flask import Blueprint

message = Blueprint("message", __name__, template_folder="templates", static_folder="static")

import navak_mailing.views
