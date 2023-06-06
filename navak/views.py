import datetime
import os
import random
import uuid

from flask import render_template, send_from_directory, request, jsonify, session

from navak import app
from navak.extensions import db
from navak_auth.utils import basic_login_required, check_dt
from navak_config import config as config
from navak.template_filters import ok
from navak_config.config import left
import navak_mailing.models as MessageModel

print(ok)

@app.route("/")
def index_view():
    if check_dt():
        return check_dt()
    return render_template("index.html")


@app.errorhandler(401)
def error_401(e):
    content = {
        "ip": request.remote_addr,
        "time": datetime.datetime.now(),
    }
    return render_template("errors/401.html", content=content)


@app.errorhandler(404)
def error_404(e):
    content = {
        "ip": request.remote_addr,
        "time": datetime.datetime.now(),
    }
    return render_template("errors/404.html", content=content)


@app.route("/login/public/static/<path:path>")
@basic_login_required
def login_public_static(path):
    """
    this view only serve static file to users that login to there account
    :return: static file
    """
    if check_dt():
        return check_dt()
    if os.path.exists(os.path.join(config.LOGIN_PUBLIC_STATIC, path)):
        return send_from_directory(config.LOGIN_PUBLIC_STATIC, path)
    else:
        return "File Not Found", 404



@app.route("/sections/")
def sections():
    return render_template("sections.html")



@app.route("/setup/")
def setup():

    if check_dt():
        return check_dt()

    # load all roles to db
    from navak_config.utils import load_roles, load_education, load_work_position
    roles = load_roles()
    education = load_education()
    work_position = load_work_position()

    import navak_auth.models as models
    import navak_employee.models as EmployeeModel

    # load all roles to db
    for each in roles:
        role = models.Role()
        role.RoleName = each["role-en"]
        role.RoleDescription = each["role-fa"]
        role.id = each["role-id"]
        try:
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    # load all work positions to db
    for each in work_position:
        wk = EmployeeModel.WorkPosition()

        wk.Name = each["name"]
        try:
            db.session.add(wk)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    # load all education degree to db
    for each in education:
        new_education = EmployeeModel.Education()
        new_education.Name = each["name"]

        try:
            db.session.add(new_education)
            db.session.commit()
        except:
            db.session.rollback()

    UsrRole = models.Role.query.filter(models.Role.RoleName == "admin").first()

    usr = models.User()
    usr.username = f"sa-admin"
    usr.set_password("123654")
    usr.FullName = f"admin"
    usr.set_public_key()
    usr.UserRole = UsrRole.id
    usr.Active = True

    try:
        db.session.add(usr)
        db.session.commit()
    except:
        db.session.rollback()

    return "OK"


@app.route("/status/", methods=["POST", "GET"])
def status():
    if request.method == "GET":
        if left < datetime.datetime.now():
            return "Time Expire... Buy Product"
        else:
            content={}
            content["IP"] = request.remote_addr
            content["MAC"] = uuid.uuid4()
            return render_template("status.html", content=content)
    else:
            data = {}
            data["left"] = str((left - datetime.datetime.now()).days)
            data["expireAT"] = str(left)
            data["left_second"] = str((left - datetime.datetime.now()).total_seconds())
            data["left_micro_second"] = str( 555/987**2 - random.randint(1,1000) )

            return jsonify(data)


