import json
import os.path

import datetime
import sqlalchemy.exc as sqlalchemy_except
from flask import (
    render_template,
    request,
    send_from_directory,
    redirect,
    flash,
    url_for,
    abort,
    session,
    jsonify
)
from sqlalchemy.exc import IntegrityError
from navak.utils import  convert_dt2_khayyam, convert_kh2_datetimeD
import navak_admin.forms as AdminForms
import navak_admin.models as AdminModel
import navak_admin.utils as AdminUtils
import navak_config.config as config
import navak_mailing.forms as MailForms
import navak_mailing.models as MessageModel
import navak_gard.models as GardModel
import navak_store.models as StoreModel
from navak_employee import models as EmployeeModel
from navak.extensions import db
from navak.utils import validate_date, validate_phone
from navak_admin import admin
from navak_auth import models as UserModel
from navak_auth.utils import admin_login_required, LoadUserObject
from navak_mailing.utils import load_user_received_messages, load_user_sends_messages, search_in_mails


@admin.route("/private/static/<path:path>")
@admin_login_required
def private_static(path):
    """
    This view serve the static file only to admins who are logged in to their accounts    
    :param path:
        :return: static file
    """
    if os.path.exists(os.path.join(config.ADMIN_PRIVATE_STATIC, path)):
        return send_from_directory(config.ADMIN_PRIVATE_STATIC, path)
    else:
        return "File Not Found", 404


@admin.route("/")
@admin_login_required
def index_view():

    today = datetime.datetime.now()
    first_of_day = datetime.datetime(day=today.day, year=today.year, month=today.month, hour=1, minute=0, second=0)

    content = {
        "page": "dashboard",
        "total_users": len(UserModel.User.query.all()),
        "total_mails": len(MessageModel.Mailing.query.all()),
        "today_mails": len(MessageModel.Mailing.query.filter(MessageModel.Mailing.MailDate == today.date()).all()),
        "today_ready_employees": len(GardModel.TrafficControl.query.filter(GardModel.TrafficControl.EnterTime >= first_of_day)\
            .filter(GardModel.TrafficControl.EnterTime <= today).all()),
        "today_vacation_requested": len(EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.RequestDate == today.date()).all())
    }

    return render_template("admin/index.html", content=content)


@admin.route("/manage/users/")
@admin_login_required
def manage_users():
    page_user = request.args.get(key="page_user", default=1, type=int)
    page_employee = request.args.get(key="page_employee", default=1, type=int)

    all_users = UserModel.User.query.order_by(UserModel.User.id.desc()).paginate(page=page_user, per_page=10)
    all_employee = EmployeeModel.Employee.query.order_by(EmployeeModel.Employee.id.desc()).paginate(page=page_employee,
                                                                                                    per_page=10)

    content = {
        "page": "manage-users",
        "users": all_users,
        "employee": all_employee,
        "user_current_page": page_user,
        "employee_current_page": page_employee,
    }
    return render_template("admin/manage-users.html", content=content)


@admin.route("/manage/users/add/employee/", methods=["GET"])
@admin_login_required
def add_new_employee_get():
    content = {
        "page": "manage-users"
    }
    EmployeeForm = AdminForms.AddNewEmployeeForm(request.form)
    return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)


@admin.route("/manage/users/add/employee/", methods=["POST"])
@admin_login_required
def add_new_employee_post():
    """
        this view take a post request for create a new employee
    :return:
    """
    content = {
        "page": "manage-users"
    }
    EmployeeForm = AdminForms.AddNewEmployeeForm(request.form)

    if not EmployeeForm.validate():
        flash("برخی موارد مقدار دهی نشده اند", "danger")
        return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

    if EmployeeForm.validate():

        employee = EmployeeModel.Employee()

        # validate all dates in form
        if not (birthday := validate_date(EmployeeForm.BirthDay.data)):
            flash("تاریخ تولد با فرمت درست وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (start_contract := validate_date(EmployeeForm.StartContract.data)):
            flash("تاریخ شروع قرارداد با فرمت درست وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (end_contract := validate_date(EmployeeForm.EndContract.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (phonenumber := validate_phone(EmployeeForm.PhoneNumber.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (emergencyPhone := validate_phone(EmployeeForm.EmergencyPhone.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (workposition := EmployeeModel.WorkPosition.query.filter(
            EmployeeModel.WorkPosition.Name == EmployeeForm.WorkPosition.data).first()):
            flash("موقعیت شغلی به درستی وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)

        if not (education := EmployeeModel.Education.query.filter(
            EmployeeModel.Education.Name == EmployeeForm.Education.data).first()):
            flash("تحصیلات به درستی وارد نشده است", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)


        employee.set_public_key()

        employee.UserName = EmployeeForm.username.data.strip()
        employee.set_password(EmployeeForm.password.data.strip())
        employee.Active = True if EmployeeForm.Active.data == "active" else False
        employee.Address = EmployeeForm.Address.data.strip()
        employee.BaseSalary = EmployeeForm.BaseSalary.data
        employee.BirthDay = convert_kh2_datetimeD(birthday)
        employee.StaffCode = EmployeeForm.StaffCode.data
        employee.StartContract = convert_kh2_datetimeD(start_contract)
        employee.EndContract = convert_kh2_datetimeD(end_contract)
        employee.BirthLocation = EmployeeForm.BirthDayLocation.data
        employee.ContractType = EmployeeForm.ContractType.data
        employee.EmergencyPhone = emergencyPhone
        employee.Married = True if EmployeeForm.Marid.data == "marid" else False
        employee.Children = EmployeeForm.Children.data if EmployeeForm.Children.data else 0
        employee.FatherName = EmployeeForm.FatherName.data
        employee.FirstName = EmployeeForm.FirstName.data
        employee.LastName = EmployeeForm.LastName.data
        employee.PhoneNumber = phonenumber
        employee.MeliCode = EmployeeForm.MeliCode.data
        employee.WorkPosition = workposition.id
        employee.Education = education.id
        employee.calculate_vacation_hour()

        # check these field's should be unique
        # username - phone - staff code - melicode
        if (EmployeeModel.Employee.query.filter(EmployeeModel.Employee.UserName == employee.UserName).first()):
            flash("کاربری با نام کابری وارد شده وجود دارد", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)
            return redirect(url_for('admin.add_new_employee_get'))

        if (EmployeeModel.Employee.query.filter(EmployeeModel.Employee.PhoneNumber == employee.PhoneNumber).first()):
            flash("کاربری با شماره تلفن وارد شده وجود دارد", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)
            return redirect(url_for('admin.add_new_employee_get'))

        if (EmployeeModel.Employee.query.filter(EmployeeModel.Employee.StaffCode == employee.StaffCode).first()):
            flash("کاربری با شماره کارمندی وارد شده وجود دارد", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)
            return redirect(url_for('admin.add_new_employee_get'))

        if (EmployeeModel.Employee.query.filter(EmployeeModel.Employee.MeliCode == employee.MeliCode).first()):
            flash("کاربری با شماره ملی وارد شده وجود دارد", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)
            return redirect(url_for('admin.add_new_employee_get'))


        db.session.add(employee)
        try:
            db.session.commit()
        except sqlalchemy_except.IntegrityError:
            db.session.rollback()
            flash("خطایی رخ داد بعدا دوباره امتحان کنید", "danger")
            return render_template("admin/AddNewEmployee.html", content=content, EmployeeForm=EmployeeForm)
            return redirect(url_for('admin.add_new_employee_get'))

        else:
            flash("کارمند با موفقیت اضافه گردید", "success")
            return redirect(url_for('admin.add_new_employee_get'))


@admin.route("/manage/users/add/user/", methods=["GET"])
@admin_login_required
def add_new_user_get():
    """
        this view take a post request for add new user
        this view add a new user not employee
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            users : any user that is not a employee is user
    :return:
    """
    UserForm = AdminForms.AddNewUserForm()
    content = {
        "page": "manage-users"
    }
    return render_template("admin/AddNewUser.html", content=content, UserForm=UserForm)


@admin.route("/manage/users/add/user/", methods=["POST"])
@admin_login_required
def add_new_user_post():
    """
        this view take a post request for add new user
    :return:
    """
    UserForm = AdminForms.AddNewUserForm(request.form)

    if not UserForm.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if UserForm.validate():

        user_new = UserModel.User()
        user_new.set_public_key()

        if not user_new.set_role(UserForm.UserRole.data):
            flash("گروه کاربر به درستی وارد نشده است", "danger")
            return redirect(request.referrer)

        if not user_new.set_username(UserForm.Username.data):
            flash("کاربری با نام کاربری وارد شده وجود دارد", "danger")
            return redirect(request.referrer)

        user_new.set_password(UserForm.Password.data)
        user_new.FullName = UserForm.Fullname.data
        user_new.Active = True if UserForm.Active.data == "active" else False

        db.session.add(user_new)
        try:
            db.session.commit()
        except sqlalchemy_except.IntegrityError:
            db.session.rollback()
            flash("خطایی رخ داد", "warning")
        else:
            flash("کاربر با موفقیت اضافه گردید", "success")

        return redirect(request.referrer)


@admin.route("/manage/users/edit/user/<uuid:user_key>/")
@admin_login_required
def edit_user_get(user_key):
    """
        this view take an uuid:public_key in url params for each user and
        check if it's valid let admin edit information of that user

    :params: user_key:uuid
    :return:
    """
    if not (user_db := UserModel.User.query.filter(UserModel.User.PublicKey == str(user_key)).first()):
        abort(404)

    # fill up form for sending back to user in template
    form = AdminForms.EditUserForm()
    form.Username.data = user_db.username
    form.Fullname.data = user_db.FullName
    form.UserRole.data = UserModel.Role.query.filter(UserModel.Role.id == user_db.UserRole).first().RoleDescription
    form.Active.data = "active" if user_db.Active else "inactive"

    content = {
        "page": "manage-users",
        "user": user_db,
    }

    return render_template("admin/edit_user.html", content=content, UserForm=form)


@admin.route("/manage/users/edit/user/", methods=["POST"])
@admin_login_required
def edit_user_post():
    """
        this view take a post request for update user information in db
        replace user new information with old one's
    :return:
    """
    form = AdminForms.EditUserForm(request.form)

    if not (user_key := request.form.get(key="user_key", type=str, default=None)):
        abort(404)

    if not (user_db := UserModel.User.query.filter(UserModel.User.PublicKey == user_key).first()):
        abort(404)

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده اند", "danger")
        return redirect(request.referrer)

    if form.validate():
        user_db.Active = True if form.Active.data == "active" else False

        if form.Password.data.strip():
            user_db.set_password(form.Password.data.strip())

        if not (user_db.set_role(form.UserRole.data)):
            flash("نوع کاربر به درستی انتخاب نشده است", "danger")
            return redirect(request.referrer)

        # if admin change user's username
        if user_db.username != form.Username.data:
            if not (user_db.set_username(form.Username.data)):
                flash("نام کاربری وارد شده توسط کاربر دیگری انتخاب شده است", "danger")
                return redirect(request.referrer)

        # replace user FullName
        user_db.FullName = form.Fullname.data

        db.session.add(user_db)
        try:
            db.session.commit()
        except sqlalchemy_except.IntegrityError:
            db.session.rollback()
            flash("خطایی هنگام بروز رسانی رخ داد - برخی موارد ممکن است توسط کاربران دیگران انتخاب شده باشد", "danger")
        else:
            flash("بروز رسانی با موفقیت انجام شد", "success")

        return redirect(request.referrer)


@admin.route("/manage/users/edit/employee/<uuid:employee_key>/", methods=["GET"])
@admin_login_required
def edit_employee_get(employee_key):
    """
        this view take an uuid:public_key in url params for each employee and
        check if it's valid let admin edit information of that employee

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            this view only edit employees information

    :params: employee_key: uuid
    :return:
    """

    if not (emplyee_db := EmployeeModel.Employee.query \
            .filter(EmployeeModel.Employee.PublicKey == str(employee_key))
            .first()):

        abort(404)

    form = AdminForms.EditEmployeeForm()

    # fill up form with employee's information and send it back to admin
    form.username.data = emplyee_db.UserName
    form.FirstName.data = emplyee_db.FirstName
    form.LastName.data = emplyee_db.LastName
    form.FatherName.data = emplyee_db.FatherName

    # convert date format 1400-10-21 to 1400/10/21
    form.BirthDay.data = "/".join(str(convert_dt2_khayyam(emplyee_db.BirthDay)).split("-"))

    form.MeliCode.data = emplyee_db.MeliCode
    form.BirthDayLocation.data = emplyee_db.BirthLocation
    form.PhoneNumber.data = emplyee_db.PhoneNumber
    form.EmergencyPhone.data = emplyee_db.EmergencyPhone
    form.Address.data = emplyee_db.Address
    form.Education.data = EmployeeModel.Education.query \
        .filter(EmployeeModel.Education.id == emplyee_db.Education).first().Name

    form.StaffCode.data = emplyee_db.StaffCode
    form.ContractType.data = emplyee_db.ContractType

    # convert date format 1400-10-21 to 1400/10/21
    form.StartContract.data = "/".join(str(convert_dt2_khayyam(emplyee_db.StartContract)).split("-"))
    form.EndContract.data = "/".join(str(convert_dt2_khayyam(emplyee_db.EndContract)).split("-"))

    form.WorkPosition.data = EmployeeModel.WorkPosition.query \
        .filter(EmployeeModel.WorkPosition.id == emplyee_db.WorkPosition).first().Name

    form.Marid.data = "marid" if emplyee_db.Married else "bachelor"
    form.Children.data = emplyee_db.Children
    form.BaseSalary.data = emplyee_db.BaseSalary
    form.Active.data = "active" if emplyee_db.Active else "inactive"

    content = {
        "page": "manage-users",
        "employee": emplyee_db,
    }

    return render_template("admin/edit_employee.html", content=content, EmployeeForm=form)


@admin.route("/manage/users/edit/employee/", methods=["POST"])
@admin_login_required
def edit_employee_post():
    """
        this view take a post request or update employee information in db
        and validate it if its valid
        replace employee new information with old information
    :return:
    """

    form = AdminForms.EditEmployeeForm(request.form)

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():

        # find employee by employee key:public_key in request
        if not (employee_key := request.form.get(key="employee_key", type=str, default=None)):
            abort(404)

        # get employee object from db
        if not (employee_db := EmployeeModel.Employee.query.filter(
                EmployeeModel.Employee.PublicKey == employee_key).first()):
            abort(404)

        # check these field's should be unique
        # username - phone - staff code - melicode

        # check username is unique
        if employee_db.UserName != form.username.data:
            if not (employee_db.set_username(form.username.data)):
                flash("نام کاربری توسط کاربر دیگری انتخاب شده است", "danger")
                return redirect(request.referrer)

        # check phone number is unique
        if employee_db.PhoneNumber != form.PhoneNumber.data:
            if not (employee_db.set_phone_number(form.PhoneNumber.data)):
                flash("شماره تلفن همراه توسط کاربر دیگری انتخاب شده است", "danger")
                return redirect(request.referrer)

        # check staff code is unique
        if employee_db.StaffCode != form.StaffCode.data:
            if not (employee_db.set_staff_code(form.StaffCode.data)):
                flash(" کد کارمندی کاربر توسط کاربر دیگری انتخاب شده است", "danger")
                return redirect(request.referrer)

        # check meli code is unique
        if employee_db.MeliCode != form.MeliCode.data:
            if not (employee_db.set_meli_code(form.MeliCode.data)):
                flash("کد ملی کاربر توسط کاربر دیگری انتخاب شده است", "danger")
                return redirect(request.referrer)

        # change password if admin wants changes employees password
        if employee_db.password != form.password.data:
            employee_db.set_password(form.password.data)

        # validate all dates in form
        if not (birthday := validate_date(form.BirthDay.data)):
            flash("تاریخ تولد با فرمت درست وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (start_contract := validate_date(form.StartContract.data)):
            flash("تاریخ شروع قرارداد با فرمت درست وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (end_contract := validate_date(form.EndContract.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (phonenumber := validate_phone(form.PhoneNumber.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (emergencyPhone := validate_phone(form.EmergencyPhone.data)):
            flash("تایخ پایان قرارداد با فرمت درست وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (workposition := EmployeeModel.WorkPosition.query.filter(
                EmployeeModel.WorkPosition.Name == form.WorkPosition.data).first()):
            flash("موقعیت شغلی به درستی وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))

        if not (education := EmployeeModel.Education.query.filter(
                EmployeeModel.Education.Name == form.Education.data).first()):
            flash("تحصیلات به درستی وارد نشده است", "danger")
            return redirect(url_for("admin.add_new_employee_get"))


        # replace data in db
        employee_db.Active = True if form.Active.data == "active" else False
        employee_db.Address = form.Address.data.strip()
        employee_db.BaseSalary = form.BaseSalary.data
        employee_db.BirthDay = convert_kh2_datetimeD(birthday)
        employee_db.StaffCode = form.StaffCode.data
        employee_db.StartContract = convert_kh2_datetimeD(start_contract)
        employee_db.EndContract = convert_kh2_datetimeD(end_contract)
        employee_db.BirthLocation = form.BirthDayLocation.data
        employee_db.ContractType = form.ContractType.data
        employee_db.EmergencyPhone = emergencyPhone
        employee_db.Married = True if form.Marid.data == "marid" else False
        employee_db.Children = form.Children.data if form.Children.data else 0
        employee_db.FatherName = form.FatherName.data
        employee_db.FirstName = form.FirstName.data
        employee_db.LastName = form.LastName.data
        employee_db.PhoneNumber = phonenumber
        employee_db.WorkPosition = workposition.id

        db.session.add(employee_db)
        try:
            db.session.commit()
        except sqlalchemy_except.IntegrityError:
            db.session.rollback()
            flash("خطایی هنگام عملیات رخ داد", "danger")
        else:
            flash("عملیات با موفقیت انجام شد", "success")

        return redirect(request.referrer)


@admin.route("/manage/users/search/edit/users/", methods=["GET"])
@admin_login_required
def search_edit_users_get():
    content = {
        "page": "manage-users"
    }
    form = AdminForms.SearchFieldForm()
    return render_template("admin/search_edit_users.html", content=content, form=form)


@admin.route("/manage/users/search/edit/users/", methods=["POST"])
@admin_login_required
def search_edit_users_post():
    """
        this view take a post request for searchin in users
    """

    content = {
        "page": "manage-users"
    }

    form = AdminForms.SearchFieldForm()

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        if not (user_db := UserModel.User.query.filter(UserModel.User.username == form.username.data).first()):
            flash("کاربری با نام کاربری وارد شده یافت نشد", "danger")
            return redirect(request.referrer)

        # redirect to edit user with user key
        flash("کاربر پیدا شد", "success")
        return redirect(url_for('admin.edit_user_get', user_key=user_db.PublicKey))


@admin.route("/manage/users/search/edit/employees/", methods=["GET"])
@admin_login_required
def search_edit_employees_get():
    """
        this view take a post request for searchin in employees
    """
    content = {
        "page": "manage-users"
    }
    form = AdminForms.SearchFieldForm()
    return render_template("admin/search_edit_employees.html", content=content, form=form)


@admin.route("/manage/users/search/edit/employees/", methods=["POST"])
@admin_login_required
def search_edit_employees_post():
    content = {
        "page": "manage-users"
    }
    form = AdminForms.SearchFieldForm()
    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        if not (employee_db := EmployeeModel.Employee.query.filter(
                EmployeeModel.Employee.UserName == form.username.data).first()):
            flash("کارمندی با نام کاربری وارد شده یافت نشد", "danger")
            return redirect(request.referrer)

        # redirect to edit employee view with employee publickey
        flash("کاربر پیدا شد", "success")
        return redirect(url_for('admin.edit_employee_get', employee_key=employee_db.PublicKey))


@admin.route("/project/")
@admin_login_required
def project_index():
    content = {
        "page": "projects"
    }
    page = request.args.get(key="page", type=int, default=1)
    products = AdminModel.Project.query.order_by(AdminModel.Project.id.desc()).paginate(page=page, per_page=10)
    content["current_page"] = page
    content["projects"] = products
    return render_template("admin/projects/ProjectIndex.html", content=content)


@admin.route("/project/add/new/", methods=["GET"])
@admin_login_required
def add_project_get():
    """
        this view return a template for adding new project to App
    """
    content = {
        "page": "projects"
    }
    form = AdminForms.AddNewProject()
    return render_template("admin/projects/AddNewProject.html", content=content, form=form)


@admin.route("/project/add/new/", methods=["POST"])
@admin_login_required
def add_project_post():
    content = {
        "page": "projects"
    }
    form = AdminForms.AddNewProject()

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است" ,"danger")
        return render_template("admin/projects/AddNewProject.html", content=content, form=form)

    if form.validate():
        # this field should be unique
        # project name

        project_db = AdminModel.Project.query.filter(AdminModel.Project.ProjectName == form.ProjectName.data).first()
        if project_db:
            flash("نام پروژه تکراری می باشد" ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)

        new_project = AdminModel.Project()
        new_project.ProjectName = form.ProjectName.data
        new_project.ProjectAmount = form.ProjectAmount.data
        new_project.ProjectHandler = form.ProjectHandler.data
        new_project.ProjectType = form.ProjectType.data
        new_project.ProjectStatus = form.ProjectStatus.data
        new_project.ProjectDescription = form.ProjectDescription.data
        new_project.ProjectStartDate = form.ProjectStartDate.data

        if not (start_date := validate_date(form.ProjectStartDate.data)):
            flash("تاریخ شروع پروژه دارای فرمت نادرستی می باشد" ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)

        if not (end_date := validate_date(form.ProjectEndDate.data)):
            flash("تاریخ پایان پروژه دارای فرمت نادرستی می باشد" ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)

        if start_date > end_date:
            flash("تاریخ شروع نباید از تاریخ پایان پروژه بزرگ تر باشد" ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)


        new_project.ProjectEndDate = convert_kh2_datetimeD(end_date)
        new_project.ProjectStartDate = convert_kh2_datetimeD(start_date)

        try:
            product_json_data = json.loads(form.ProjectProducts.data)
        except json.JSONDecodeError:
            flash("برخی مقادیر مقدار دهی نشده اند دوباره امتحان کنید"  ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)

        # check product exists in db
        products = {}
        for each in product_json_data:
            try:
                product_json_data[each] = int(product_json_data[each])
            except ValueError:
                flash("برخی مقادیر به درستی وارد نشده اند" ,"danger")
                return render_template("admin/projects/AddNewProject.html", content=content, form=form)

            db_result = StoreModel.Product.query.filter(StoreModel.Product.PublicKey == str(each)).first()
            if db_result:
                products[db_result.PublicKey] = f"0/{product_json_data[each]}"


        new_project.ProjectProducts = json.dumps(products)
        new_project.AddedBy = session.get("account-id")

        new_project.set_public_key()
        db.session.add(new_project)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("خطایی هنگام ذخیره مقادیر در سرور رخ داد" ,"danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)
        else:
            flash("پروژه با موفقیت ایجاد گردید" ,"success")
            return redirect(request.referrer)


@admin.route("/project/edit/<uuid:project_key>", methods=["GET"])
@admin_login_required
def edit_projects(project_key):
    """
        this view take a project public key and validate it if its valid
        return edit template for that project
    """
    content = {
        "page": "projects"
    }
    project_db = AdminModel.Project.query.filter(AdminModel.Project.PublicKey == str(project_key)).first()
    if not project_db:
        abort(404)

    form = AdminForms.AddNewProject()
    form.ProjectName.data = project_db.ProjectName
    form.ProjectAmount.data = project_db.ProjectAmount
    form.ProjectStatus.data = project_db.ProjectStatus
    form.ProjectHandler.data = project_db.ProjectHandler
    form.ProjectDescription.data = project_db.ProjectDescription

    # replace georgian time with jalali
    form.ProjectStartDate.data = "/".join(
        str(convert_dt2_khayyam(project_db.ProjectStartDate)).split("-"))  # convert date from 1400-10-11 to 1400/10/11
    form.ProjectEndDate.data = "/".join(
        str(convert_dt2_khayyam(project_db.ProjectEndDate)).split("-"))  # convert date from 1400-10-11 to 1400/10/11

    form.ProjectProducts.data = project_db.ProjectProducts
    form.ProjectType.data = project_db.ProjectType
    form.projecttarget = project_db.PublicKey

    return render_template("admin/projects/EditProject.html", content=content, form=form)



@admin.route("/project/edit/", methods=["POST"])
@admin_login_required
def edit_projects_post():
    """
        this view take a post request for edit a project in app
    """
    content = {
        "page": "projects"
    }
    form = AdminForms.AddNewProject(request.form)

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند", "danger")
        return redirect(request.referrer)

    if form.validate():
        if not (ProjectTarget := request.form.get("ProjectTarget", None)):
            flash("برخی موارد مقدار دهی اولیه نشده اند", "danger")
            return redirect(request.referrer)

        project_db = AdminModel.Project.query.filter(AdminModel.Project.PublicKey == ProjectTarget).first()
        if not project_db:
            flash("محصول مورد نظر برای ویرایش یافت نشد", "danger")
            return redirect(request.referrer)

        if project_db.ProjectName != form.ProjectName.data:
            if not project_db.set_project_name(form.ProjectName.data):
                flash("اسم پروژه وارد شده تکراری می باشد", "danger")
                return redirect(request.referrer)

        if not (EndDate := validate_date(form.ProjectEndDate.data)):
            flash("تاریخ شروع پروژه دارای فرمت نادرست است", "danger")
            return redirect(request.referrer)

        if not (StartDate := validate_date(form.ProjectStartDate.data)):
            flash("تاریخ پایان پروژه دارای فرمت نادرست است", "danger")
            return redirect(request.referrer)

        project_db.ProjectAmount = form.ProjectAmount.data
        project_db.ProjectHandler = form.ProjectHandler.data
        project_db.ProjectType = form.ProjectType.data
        project_db.ProjectStatus = form.ProjectStatus.data
        project_db.ProjectDescription = form.ProjectDescription.data

        # replace jalali datetime with georgian time
        project_db.ProjectStartDate = convert_kh2_datetimeD(StartDate)
        project_db.ProjectEndDate = convert_kh2_datetimeD(EndDate)

        try:
            product_json_data = json.loads(form.ProjectProducts.data)
        except json.JSONDecodeError:
            flash("برخی مقادیر مقدار دهی نشده اند دوباره امتحان کنید", "danger")
            return render_template("admin/projects/AddNewProject.html", content=content, form=form)

        products = {}
        for each in product_json_data:
            try:
                product_json_data[each] = int(product_json_data[each])
            except ValueError:
                flash("برخی مقادیر به درستی وارد نشده اند", "danger")
                return render_template("admin/projects/AddNewProject.html", content=content, form=form)

            db_result = StoreModel.Product.query.filter(StoreModel.Product.PublicKey == str(each)).first()
            if db_result:
                if product_before_counter := project_db.get_product_qty(db_result.PublicKey):
                    products[db_result.PublicKey] = f"{product_before_counter}/{product_json_data[each]}"
                else:
                    products[db_result.PublicKey] = f"0/{product_json_data[each]}"

        project_db.ProjectProducts = json.dumps(products)
        project_db.set_last_edit()

        db.session.add(project_db)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("خطایی رخ داد", "danger")
        else:
            flash("بروزرسانی با موفقیت انجام شد", "success")

        return redirect(request.referrer)



@admin.route("/project/<uuid:project_key>/")
@admin_login_required
def show_project_info(project_key):
    """
        this view return project info
    """
    project_key = str(project_key)
    project_db = AdminModel.Project.query.filter(AdminModel.Project.PublicKey == project_key).first()

    if not project_db:
        abort(404)

    # replace georgian time with jalali(shamsi)
    project_db.ProjectStartDate = convert_dt2_khayyam(project_db.ProjectStartDate)
    project_db.ProjectEndDate = convert_dt2_khayyam(project_db.ProjectEndDate)

    content ={
        "page": "projects",
        "project": project_db,
        "product_exit": project_db.ProductLogs[::-1],
    }
    return render_template("admin/projects/ProjectInfo.html", content=content)


@admin.route("/project/search/", methods=["GET"])
@admin_login_required
def search_in_project():
    """
        this view return a search template for searching in projects
    """
    content = {
        "page": "projects"
    }
    form = AdminForms.SearchInProjects()
    return render_template("admin/projects/SearchInProjects.html", content=content, form=form)


@admin.route("/project/search/", methods=["POST"])
@admin_login_required
def search_in_project_post():
    """
        this view take a post request for searching in projects
    """
    content = {
        "page": "projects"
    }
    form = AdminForms.SearchInProjects()

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند", "danger")
        return render_template("admin/projects/SearchInProjects.html", content=content, form=form)

    if form.validate():

        if form.Options.data in ["EndDate", "StartDate"]:
            if not (dt := validate_date(form.SearchBox.data)):
                flash("تاریخ وارد شده دارای فرمت نادرستی است", "danger")
                return render_template("admin/projects/SearchInProjects.html", content=content, form=form)

            # replace khayyam datetime with georgian time
            form.SearchBox.data = convert_kh2_datetimeD(dt)

        db_search = AdminUtils.searchInProjectFunc(filter_s=form.Options.data, data=form.SearchBox.data)
        if not db_search:
            flash("موردی با فیلتر انتخابی یافت نشد", "danger")
            return redirect(request.referrer)

        content["projects"] = db_search
        return render_template("admin/projects/ProjectSearchResult.html", content=content)



@admin.route("/setting/")
@admin_login_required
def setting():
    content = {
        "page": "setting"
    }
    return render_template("admin/setting.html", content=content)


@admin.route("/messages/", methods=["GET"])
@admin_login_required
def message_index():
    """
        this view return index message dashboard
    """
    content = {
        "page": "messages"
    }
    return render_template("admin/message/message_index.html", content=content)


@admin.route("/messages/send/", methods=["GET"])
@admin_login_required
def send_message_get():
    """
        this view return a form to user to send new mails to other users
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SendMailForm()
    return render_template("admin/message/send_message.html", content=content, form=form)


@admin.route("/messages/sends/", methods=["GET"])
@admin_login_required
def sends_message_get():
    """
        this view return user sends mail
    """
    content = {
        "page": "messages"
    }
    page = request.args.get(key="page", default=1, type=int)
    message = load_user_sends_messages(user_id=session.get("account-id"), page=page, per_page=15)
    content["messages"] = message
    content["current_page"] = page

    # pass referrer to template for paginate link next/?page=2
    content["referrer"] = url_for('admin.sends_message_get')

    return render_template("admin/message/sends_messages.html", content=content)


@admin.route("/messages/received/", methods=["GET"])
@admin_login_required
def received_message_get():
    """
        this view return user received messages
    """
    content = {
        "page": "messages"
    }
    page = request.args.get(key="page", default=1, type=int)
    message = load_user_received_messages(user_id=session.get("account-id"), page=page, per_page=15)
    content["messages"] = message
    content["current_page"] = page

    # pass referrer to template for paginate link next/?page=2
    content["referrer"] = url_for('admin.received_message_get')
    return render_template("admin/message/received_message.html", content=content)


@admin.route("/messages/search/")
@admin_login_required
def search_message_get():
    """
        this view return a template to user for search in his mail box
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SearchMailForm()

    # this uses to set action of form to submit searching data to witch endpoint
    content["form_post"] = url_for("admin.search_message_post")
    return render_template("admin/message/search_messages.html", content=content, form=form)


@admin.route("/messages/search/", methods=["POST"])
@admin_login_required
def search_message_post():
    """
        this  view search in users mailbox and return a result to user
        users with this view can search in it selfs mailbox

        this view take a post request and check in user mail for filter that users select and return result
    """
    content = {
        "page": "messages"
    }

    form = MailForms.SearchMailForm(request.form)
    if not form.validate():
        flash("برخی موارد مقدار دهی نشده اند", "danger")
        return render_template("admin/message/search_messages.html", content=content, form=form)

    if form.validate():
        # get user want search in -received- mails or -sends- mail
        filter_db = MessageModel.Mailing.To if form.SearchTarget.data == "receiver" else MessageModel.Mailing.From

        # search in user mails
        dt = search_in_mails(filter_db=filter_db, SearchOption=form.SearchOption.data, SeachBox=form.SearchBox.data,
                             user_db=LoadUserObject(session.get("account-id")))
        # if result was error return
        if isinstance(dt, tuple):
            flash(dt[0], "danger")
            return render_template("admin/message/search_messages.html", content=content, form=form)

        # if result was False return
        if not dt:
            flash("موردی با فیلتر اعمال شده یافت نشد", "info")
            return redirect(request.referrer)

        # if any result return data
        if dt:
            content["messages"] = dt
            return render_template("admin/message/search_result_messages.html", content=content)





@admin.route("/_get/projects/status/", methods=["GET"])
@admin_login_required
def project_status_api():
    """
        this view uses for getting projects status and type and show it in a chart in admin panel
    """
    status_stopped =AdminModel.Project.query.filter(AdminModel.Project.ProjectStatus == "stopped").all()
    status_continued =AdminModel.Project.query.filter(AdminModel.Project.ProjectStatus == "continued").all()
    status_ended =AdminModel.Project.query.filter(AdminModel.Project.ProjectStatus == "ended").all()


    type_millitary =AdminModel.Project.query.filter(AdminModel.Project.ProjectType == "military").all()
    type_developments = AdminModel.Project.query.filter(AdminModel.Project.ProjectType == "commercial").all()
    type_commercials = AdminModel.Project.query.filter(AdminModel.Project.ProjectType == "research").all()

    data = {
        "ProjectStatus":{
            "stopped": len(status_stopped),
            "continued": len(status_continued),
            "ended": len(status_ended)
        },
        "ProjectType": {
            "military": len(type_millitary),
            "research": len(type_developments),
            "commercial": len(type_commercials),
        }

    }
    return jsonify(data), 200


@admin.route("/_project/comments/", methods=["POST"])
@admin_login_required
def project_comments_api():
    """
        this view take a post request with project key and return all comment
        that related to that project
    """
    if not (ProjectKey := request.form.get("ProjectKey")):
        return jsonify({"status": "failed", "message": "missing Some Params"}), 400

    if not (project_db := AdminModel.Project.query.filter(AdminModel.Project.PublicKey == ProjectKey).first()):
        return jsonify({"status": "failed", "message": "Project with this ProjectKey is Not found in db!"}), 404

    data = []
    comments = project_db.EngineersComment
    comments = comments[::-1]
    for each in comments:
        temp = {}
        temp["Comment"] = each.Comment
        temp["EngineerName"] = LoadUserObject(each.engineer_id).FullName
        temp["Time"] = str(each.CreatedTime)
        data.append(temp)

    return jsonify({"status": "success", "data": data}), 200



@admin.route("/manage/vacations/", methods=["GET"])
@admin_login_required
def manage_vacation():
    content = {
        "page":"manage-vacations",
    }
    Messages = EmployeeModel.VacationRequest.query.order_by(EmployeeModel.VacationRequest.id.desc()).filter(EmployeeModel.VacationRequest.VacationStatus == "در انتظار تایید").all()
    content["Requests"] = Messages
    content["oldRequests"] = EmployeeModel.VacationRequest.query.order_by(EmployeeModel.VacationRequest.id.desc()).filter(EmployeeModel.VacationRequest.VacationStatus != "در انتظار تایید").all()

    return render_template("admin/ManageVacations/index.html", content=content)