from flask import (session, render_template, redirect, url_for, flash, request)

import navak_auth.models as UserModel
from navak_auth import auth
from navak_auth.forms import LoginForm
from navak_config.config import LOGIN_PATHS_MATTERIAL
from navak_employee.models import Employee


@auth.route("/login/", methods=["POST"])
def login_post():
    """
        this view take a post request for login Employees to there panel
    :return: Html
    """
    form = LoginForm()

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده اند")
        return redirect(url_for("auth.employee_login_view"))

    if form.validate():
        # check user select valid login path = ["employee", "admin", "gard", "engineer", "office"],
        if form.usergroup.data not in LOGIN_PATHS_MATTERIAL[0]:
            flash("گروه انتخابی کاربر نادرست است", "danger")
            return redirect(request.referrer)

        # check user type is in ["admin", "engineer", "office", "gard"]
        if form.usergroup.data != "employee":

            if not (user_db := UserModel.User.query.filter(UserModel.User.username == form.username.data).first()):
                flash("کاربری با نام کاربری وارد شده یافت نشد", "danger")
                return redirect(request.referrer)

            if not user_db.check_password(form.password.data):
                flash("اعتبار سنجی نادرست است", "danger")
                return redirect(request.referrer)

            # check user account status
            if not user_db.Active:
                flash("حساب کاربری وارد شده غیرفعال می باشد", "danger")
                return redirect(request.referrer)

            # check user group via backref
            if user_db.Role.RoleName != form.usergroup.data:
                flash("کاربر وارد شده در گروه وارد شده نمی باشد", "danger")
                return redirect(request.referrer)

            if form.usergroup.data == "admin":
                session["login"] = True
                session["account-id"] = user_db.id
                session.permanent = True
                session["username"] = user_db.username
                session["password"] = user_db.password
                session["role"] = "admin"
                return redirect(url_for('admin.index_view'))

            elif form.usergroup.data == "store":
                session["login"] = True
                session["account-id"] = user_db.id
                session.permanent = True
                session["username"] = user_db.username
                session["password"] = user_db.password
                session["role"] = "store"
                return redirect(url_for('store.index_view'))

            elif form.usergroup.data == "engineer":
                session["login"] = True
                session["account-id"] = user_db.id
                session.permanent = True
                session["username"] = user_db.username
                session["password"] = user_db.password
                session["role"] = "engineer"
                return redirect(url_for('engineer.index_view'))

            elif form.usergroup.data == "gard":
                session["login"] = True
                session["account-id"] = user_db.id
                session.permanent = True
                session["username"] = user_db.username
                session["password"] = user_db.password
                session["role"] = "gard"
                return redirect(url_for('gard.index_view'))


        # if user select employee group type
        else:
            if not (Employee_db := Employee.query.filter(Employee.UserName == form.username.data).first()):
                flash("کاربری با نام کاربری وارد شده یافت نشد", "danger")
                return redirect(request.referrer)

            if not Employee_db.check_password(form.password.data):
                flash("اعتبار سنجی نادرست است", "danger")
                return redirect(request.referrer)

            session["login"] = True
            session["account-id"] = Employee_db.id
            session.permanent = True
            session["username"] = Employee_db.UserName
            session["password"] = Employee_db.password
            session["role"] = "employee"
            return redirect(url_for("employee.index_view"))

        # otherwise redirect user to login page
        return redirect(request.referrer)


@auth.route("/login/")
def login_view():
    """Users Login"""
    form = LoginForm()
    return render_template("auth/login.html", form=form)


@auth.route("/logout/")
def logout_view():
    """logout users"""
    session.clear()
    return redirect(url_for("index_view"))
