from flask import Blueprint


employee = Blueprint("employee", __name__, static_folder="static", template_folder="templates")
import navak_employee.views
