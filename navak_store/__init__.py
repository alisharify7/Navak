from flask import Blueprint

store = Blueprint("store", __name__, static_folder="static", template_folder="templates")

import navak_store.views
