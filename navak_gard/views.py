import os.path

import khayyam
from flask import render_template, send_from_directory, jsonify, request, flash, redirect, session, url_for

from navak_gard import gard
from navak.extensions import  db
import navak_gard.models as GardModel
from navak_auth.utils import gard_login_required
from navak_config.config import GARD_PRIVATE_STATIC
import navak_employee.models as EmployeeModel
import navak_gard.forms as GardForms
import navak_mailing.forms as MailForms
from  navak_mailing.utils import load_user_sends_messages, load_user_received_messages,search_in_mails
import navak_mailing.models as MessageModel
from navak_auth.utils import LoadUserObject


@gard.route("/private/static/<path:path>")
@gard_login_required
def private_static(path):
    if os.path.exists(GARD_PRIVATE_STATIC / path):
        return send_from_directory(GARD_PRIVATE_STATIC, path)
    else:
        return "File Not Found!", 404

@gard.route("/")
@gard_login_required
def index_view():
    content = {
        "page": "dashboard"
    }
    return render_template("gard/index.html", content=content)


@gard.route("/Register/Traffic/")
@gard_login_required
def register_traffic_get():
    content = {
        "page": "report-traffic"
    }
    return render_template("gard/register-traffic.html", content=content)



@gard.route("/Employee/Register/")
@gard_login_required
def employee_register_traffic():
    content = {
        "page": "report-traffic"
    }
    return render_template("gard/register_employee_traffic.html", content=content)



@gard.route("/setting/")
@gard_login_required
def setting():
    content = {
        "page": "setting"
    }
    return render_template("gard/setting.html", content=content)


@gard.route("/Guest/Register/")
@gard_login_required
def guest_register():
    content = {
        "page": "report-traffic"
    }

    page = request.args.get(key="page", default=1, type=int)
    form = GardForms.RegisterGuestTraffic()

    today = khayyam.JalaliDatetime.now()
    first_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=1, minute=0, second=0)

    today_guests = GardModel.GuestTrafficControl.query.filter(GardModel.GuestTrafficControl.EnterTime >= first_of_day)\
        .filter(GardModel.GuestTrafficControl.EnterTime <= today).filter(GardModel.GuestTrafficControl.ExitTime == None).all()

    guests = GardModel.GuestTrafficControl.query.order_by(GardModel.GuestTrafficControl.id.desc()).paginate(page=page, per_page=15)

    content["guests"] = guests
    content["current_page"] = page
    content["today_guests"] = today_guests
    return render_template("gard/register_guest_traffic.html", content=content, form=form)




@gard.route("/messages/", methods=["GET"])
@gard_login_required
def message_index():
    """
        this view return index message dashboard
    """
    content = {
        "page": "messages"
    }
    return render_template("gard/message/message_index.html", content=content)


@gard.route("/messages/send/", methods=["GET"])
@gard_login_required
def send_message_get():
    """
        this view return a form to user to send new mails to other users
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SendMailForm()
    return render_template("gard/message/send_message.html", content=content, form=form)


@gard.route("/messages/sends/", methods=["GET"])
@gard_login_required
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
    content["referrer"] = url_for('gard.sends_message_get')

    return render_template("gard/message/sends_messages.html", content=content)


@gard.route("/messages/received/", methods=["GET"])
@gard_login_required
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
    content["referrer"] = url_for('gard.received_message_get')
    return render_template("gard/message/received_message.html", content=content)


@gard.route("/messages/search/")
@gard_login_required
def search_message_get():
    """
        this view return a template to user for search in his mail box
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SearchMailForm()

    # this uses to set action of form to submit searching data to witch endpoint
    content["form_post"] = url_for("gard.search_message_post")
    return render_template("gard/message/search_messages.html", content=content, form=form)


@gard.route("/messages/search/", methods=["POST"])
@gard_login_required
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
        return render_template("gard/message/search_messages.html", content=content, form=form)

    if form.validate():
        # get user want search in -received- mails or -sends- mail
        filter_db = MessageModel.Mailing.To if form.SearchTarget.data == "receiver" else MessageModel.Mailing.From

        # search in user mails
        dt = search_in_mails(filter_db=filter_db, SearchOption=form.SearchOption.data, SeachBox=form.SearchBox.data,
                             user_db=LoadUserObject(session.get("account-id")))
        # if result was error return
        if isinstance(dt, tuple):
            flash(dt[0], "danger")
            return render_template("gard/message/search_messages.html", content=content, form=form)

        # if result was False return
        if not dt:
            flash("موردی با فیلتر اعمال شده یافت نشد", "info")
            return redirect(request.referrer)

        # if any result return data
        if dt:
            content["messages"] = dt
            return render_template("gard/message/search_result_messages.html", content=content)



@gard.route("/Guest/Register/", methods=["POST"])
@gard_login_required
def guest_register_post():
    content = {
        "page": "report-traffic"
    }
    form = GardForms.RegisterGuestTraffic()

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return render_template("gard/register_guest_traffic.html", content=content, form=form)

    if form.validate():
        new_traffic = GardModel.GuestTrafficControl()
        new_traffic.set_public_key()
        new_traffic.title = form.title.data
        new_traffic.description = form.description.data
        new_traffic.set_enter_time()

        try:
            db.session.add(new_traffic)
            db.session.commit()
        except:
            db.session.rollback()
            flash("خطایی رخ داد بعدا امتحان کنید" ,"danger")
        else:
            flash("ورود با موفقیت ثبت گردید","success")

        return redirect(request.referrer)




@gard.route("/exit/guest/traffic/<uuid:key>", methods=["GET"])
@gard_login_required
def exit_guest_traffic(key):
    """
        this view take a guest traffic key and set exit time for that guest in db
    """
    guest_db = GardModel.GuestTrafficControl.query.filter(GardModel.GuestTrafficControl.PublicKey == str(key)).first()
    if not guest_db:
        flash("ورودی با کد وارد شده یافت نشد", "danger")
        return redirect(request.referrer)
    if guest_db and guest_db.ExitTime:
        flash("برای ورودی وارد شده قبلا خروج ثبت شده است", "danger")
        return redirect(request.referrer)

    guest_db.set_exit_time()
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("خطایی رخ داد" ,"danger")
    else:
        flash("خروج با موفقیت ثبت شد" ,"success")

    return redirect(request.referrer)

@gard.route("/_get/employees/", methods=["POST"])
@gard_login_required
def get_all_employee_api():
    """
        this api view take a post request and return all employees and their work position
        {
            'workposition': [
                                'employee name':name,
                                'employee key':key
                            ]
        }

    """
    work_position = []
    employees = {}

    all_work_positions = EmployeeModel.WorkPosition.query.all()
    for each in all_work_positions:
        work_position.append([each.Name, each.id])
        employees[each.Name] = []

    for WorkName, WorkIndex in work_position:
        all_employees_in_target = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.WorkPosition == WorkIndex).all()

        if all_employees_in_target:
            users = []
            for each in all_employees_in_target:
                temp ={}
                temp["name"] = each.FirstName + " " + each.LastName
                temp["key"] = each.PublicKey
                users.append(temp)
            employees[WorkName] = users

    return jsonify(employees)


@gard.route("/register/employee/traffic/", methods=["POST"])
@gard_login_required
def register_employee_api():
    """
        this api view take post request and register traffic for employee

            key = employee key
            status = (ok, cancel)
    """
    if not request.form.get("key") and not request.form.get("status"):
        return jsonify({"status": "failed", "message": "برخی مقادیر مقدار دهی نشده است"}), 400

    key = request.form.get("key")
    op = request.form.get("status")
    today = khayyam.JalaliDatetime.now()
    first_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=1, minute=0, second=0)

    employee_db = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.PublicKey == key).first_or_404()
    today_traffic = GardModel.TrafficControl.query.filter(GardModel.TrafficControl.Employee_id == employee_db.id)\
        .filter(GardModel.TrafficControl.EnterTime > first_of_day).first()

    if op == "cancel" and not today_traffic:
        return jsonify({"status":"failed", "message": "ابتدا حضور کاربر را ثبت کنید"}), 400

    if op == "cancel":
        try:
            db.session.delete(today_traffic)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"status":"failed", "message": "خطایی رخ داد"}), 400
        else:
            return jsonify({"status":"success", "message": "عملیات با موفقیت انجام شد- حضور کارمند لغو شد"}), 400

    if op == "ok" and today_traffic:
        return jsonify({"status":"success", "message": "عملیات با موفقیت انجام شد - حضور کارمند ثبت شد"}), 200

    if op == "ok" and not today_traffic:
        today_traffic = GardModel.TrafficControl()
        today_traffic.Employee_id = employee_db.id
        today_traffic.set_public_key()
        today_traffic.set_enter_time()
        db.session.add(today_traffic)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"status":"failed", "message": "خطایی رخ داد"}), 400
        else:
            return jsonify({"status":"success", "message": "عملیات با موفقیت انجام شد - حضور کارمند ثبت شد"}), 200



    return jsonify({"status":"failed", "message": "عدم"}), 400



@gard.route("/exit/employee/traffic/", methods=["POST"])
@gard_login_required
def exit_employee_api():
    """
        this api view take post request and register traffic for employee

            key = employee key
            status = (ok, cancel)
    """
    if not request.form.get("key") and not request.form.get("status"):
        return jsonify({"status": "failed", "message": "برخی مقادیر مقدار دهی نشده است"}), 400

    key = request.form.get("key")
    op = request.form.get("status")
    today = khayyam.JalaliDatetime.now()
    first_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=1, minute=0, second=0)

    employee_db = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.PublicKey == key).first_or_404()
    today_traffic = GardModel.TrafficControl.query.filter(GardModel.TrafficControl.Employee_id == employee_db.id)\
        .filter(GardModel.TrafficControl.EnterTime > first_of_day).first()

    if not today_traffic:
        return jsonify({"status":"failed", "message": "ابتدا حضور کاربر را ثبت کنید"}), 400

    if op == "cancel" and not today_traffic:
        return jsonify({"status":"failed", "message": "ابتدا حضور کاربر را ثبت کنید"}), 400

    if op == "cancel":
        today_traffic.ExitTime = None
        db.session.add(today_traffic)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"status":"failed", "message": "خطایی رخ داد"}), 400
        else:
            return jsonify({"status":"success", "message": "عملیات با موفقیت انجام شد- خروج کارمند لغو شد"}), 400

    if op == "ok" and today_traffic:
        today_traffic.set_exit_time()
        db.session.add(today_traffic)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"status":"failed", "message": "خطایی رخ داد"}), 400
        else:
            return jsonify({"status":"success", "message": "عملیات با موفقیت انجام شد- خروج کارمند با موفقیت انجام شد"}), 200


    if op == "ok" and not today_traffic:
        return jsonify({"status":"failed", "message": "ابتدا حضور کاربر را ثبت کنید"}), 400




    return jsonify({"status":"failed", "message": "عدم"}), 400


@gard.route("/today/status/traffic/", methods=["POST"])
@gard_login_required
def today_registered_employees():
    """
        this view return a status for employees traffic for now
    """
    today = khayyam.JalaliDatetime.now()
    first_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=1, minute=0, second=0)
    now_employees = GardModel.TrafficControl.query.filter(GardModel.TrafficControl.EnterTime > first_of_day).all()
    employees = {}

    workposition = EmployeeModel.WorkPosition.query.all()
    for each in workposition:
        employees[each.Name] = []


    for each in now_employees:
        employee_db = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.id == each.Employee_id).first()
        temp = {}
        temp["name"] = employee_db.FirstName + " " + employee_db.LastName
        temp["key"] = employee_db.PublicKey
        temp["enter"] = 1 if each.EnterTime else 0
        temp["exit"] = 1 if each.ExitTime else 0
        employees[EmployeeModel.WorkPosition.query.filter(EmployeeModel.WorkPosition.id == employee_db.WorkPosition).first().Name].append(temp)


    return jsonify(employees)

