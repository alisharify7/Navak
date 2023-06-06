import os.path

from flask import render_template, request, redirect, flash, url_for, session, send_from_directory, jsonify

import navak_admin.models as AdminModel
import navak_engineer.forms as EngineerForms
import navak_engineer.models as EngineerModel
import navak_mailing.forms as MailForms
import navak_mailing.models as MessageModel
from navak.extensions import db
from navak_auth.utils import engineer_only_view, LoadUserObject, request_handler_only_view
from navak_engineer import engineer
from navak_mailing.utils import load_user_sends_messages, search_in_mails, load_user_received_messages
import navak_employee.models as EmployeeModel
import navak_auth.models as AuthModel
from navak_config.config import ENGINEER_PRIVATE_STATIC



@engineer.route("/private/static/<path:path>")
@engineer_only_view
def private_static(path):
    """
        this view serve static file that are related to engineers
        and only serve it for user that is enigneer
    """
    if os.path.exists(ENGINEER_PRIVATE_STATIC / path):
        return send_from_directory(ENGINEER_PRIVATE_STATIC, path)
    else:
        return "File Not Found !", 404



@engineer.route("/")
@engineer_only_view
def index_view():
    content = {
        "page": "dashboard"
    }
    return render_template("engineer/index.html", content=content)


@engineer.route("/messages/", methods=["GET"])
@engineer_only_view
def message_index():
    """
        this view return index message dashboard
    """
    content = {
        "page": "messages"
    }
    return render_template("engineer/message/message_index.html", content=content)


@engineer.route("/messages/send/", methods=["GET"])
@engineer_only_view
def send_message_get():
    """
        this view return a form to user to send new mails to other users
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SendMailForm()
    return render_template("engineer/message/send_message.html", content=content, form=form)


@engineer.route("/messages/sends/", methods=["GET"])
@engineer_only_view
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
    content["referrer"] = url_for('engineer.sends_message_get')

    return render_template("engineer/message/sends_messages.html", content=content)


@engineer.route("/messages/received/", methods=["GET"])
@engineer_only_view
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
    content["referrer"] = url_for('engineer.received_message_get')
    return render_template("engineer/message/received_message.html", content=content)


@engineer.route("/messages/search/")
@engineer_only_view
def search_message_get():
    """
        this view return a template to user for search in his mail box
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SearchMailForm()

    # this uses to set action of form to submit searching data to witch endpoint
    content["form_post"] = url_for("engineer.search_message_post")
    return render_template("engineer/message/search_messages.html", content=content, form=form)


@engineer.route("/messages/search/", methods=["POST"])
@engineer_only_view
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
        return render_template("engineer/message/search_messages.html", content=content, form=form)

    if form.validate():
        # get user want search in -received- mails or -sends- mail
        filter_db = MessageModel.Mailing.To if form.SearchTarget.data == "receiver" else MessageModel.Mailing.From

        # search in user mails
        dt = search_in_mails(filter_db=filter_db, SearchOption=form.SearchOption.data, SeachBox=form.SearchBox.data,
                             user_db=LoadUserObject(session.get("account-id")))
        # if result was error return
        if isinstance(dt, tuple):
            flash(dt[0], "danger")
            return render_template("engineer/message/search_messages.html", content=content, form=form)

        # if result was False return
        if not dt:
            flash("موردی با فیلتر اعمال شده یافت نشد", "info")
            return redirect(request.referrer)

        # if any result return data
        if dt:
            content["messages"] = dt
            return render_template("engineer/message/search_result_messages.html", content=content)


@engineer.route("/projects/")
@engineer_only_view
def manage_projects():
    content = {
        "page": "projects"
    }
    form=EngineerForms.SearchInProjects()
    return render_template("engineer/Project/Manage-Project.html", content=content, form=form)


@engineer.route("/projects/", methods=["POST"])
@engineer_only_view
def manage_projects_post():
    """
        this view take a post request and check if its valid project id
        return a all comments
    """
    content = {
        "page": "projects"
    }
    form=EngineerForms.SearchInProjects()
    if not form.validate():
        flash("برخی موارد مقداردهی اولیه نشده است" ,"danger")
        return redirect(request.referrer)

    if form.validate():

        project_db = AdminModel.Project.query.filter(AdminModel.Project.id == form.SearchBox.data).first()
        if not project_db:
            flash("پروژه با شماره پیگیری مورد نظر یافت نشد", "danger")
            return redirect(request.referrer)

        if project_db.ProjectStatus != "continued":
            flash("وضعیت پروژه در وضعیتی غیر از در حال انجام است", "danger")
            return redirect(request.referrer)

        userObject = LoadUserObject(session.get("account-id"))
        content["comments"] = userObject.EngineerComments[::-1]
        content["project"] = project_db
        form = EngineerForms.AddCommentProject()
        form.ProjectKey.data = project_db.PublicKey
        return render_template("engineer/Project/ProjectComments.html", content=content, form=form)


@engineer.route("/register/project/status/", methods=["POST"])
@engineer_only_view
def register_project_comments_post():
    """
        this view  take a post request for add new comment about a project
    """
    form = EngineerForms.AddCommentProject()

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        # check project key is valid and its in continued status
        project_db = AdminModel.Project.query.filter(AdminModel.Project.PublicKey == form.ProjectKey.data).first()
        if not project_db:
            flash("پروژه مورد نظر یافت نشد", "danger")
            return redirect(request.referrer)

        if project_db.ProjectStatus != "continued":
            flash("پروژه مورد نظر در وضعیتی غیر از درحال انجام است", "danger")
            return redirect(request.referrer)

        project_cm = EngineerModel.ProjectComments()
        project_cm.project_id = project_db.id
        project_cm.Comment = form.Comment.data
        project_cm.engineer_id = session.get("account-id")

        db.session.add(project_cm)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("خطایی حین عملیات رخ داد", "danger")
        else:
            flash("عملیات با موفقیت انجام شد", "success")

        return redirect(request.referrer)


@engineer.route("/setting/")
@engineer_only_view
def setting_view():
    content = {
        "page": "setting"
    }
    return render_template("engineer/setting.html", content=content)

@engineer.route("/vacation/")
@request_handler_only_view
def request_vacation():
    content = {
        "page": "vacation"
    }
    vacation_page = request.args.get(key="page", type=int, default=1)

    engineer_db = LoadUserObject(session.get("account-id"))
    workposition = AdminModel.VacationRequestHandler.query.filter(AdminModel.VacationRequestHandler.UserId == engineer_db.id).first()

    VacationRequest = EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.WorkPositionId == workposition.WorkPositionId)\
        .filter(EmployeeModel.VacationRequest.VacationStatus == "در انتظار تایید")\
            .order_by(EmployeeModel.VacationRequest.id.desc())\
                .paginate(per_page=15, page=vacation_page)

    content["Requests"] = VacationRequest
    return render_template("engineer/RequestVacation.html", content=content)



@engineer.route("/set/vacation/", methods=["POST"])
@request_handler_only_view
def set_vacation_api():
    """
        this view take a post request for approve or reject a vacation request
        this view only response to admin or engineer with required rule
    """

    if not request.form.get("key") or not request.form.get("opration"):
        return jsonify({"status": "failed", "message": "برخی موارد مقدار نشده است"}), 400

    op = request.form.get("opration")
    key = request.form.get("key")

    if len(key) != 36:
        return jsonify({"status": "failed", "message": "برخی موارد مقدار نشده است"}), 400

    if op not in ["approve", "reject"]:
        return jsonify({"status": "failed", "message": "برخی موارد مقدار نشده است"}), 400


    # get admin user object
    UserDB = LoadUserObject(session.get("account-id"))

    # get request vacation object
    VacationRequest = EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.PublicKey == key).first()
    if not VacationRequest:
        return jsonify({"status": "failed", "message":"درخواست مرخصی با کد مربوطه یافت نشد"}), 400


    Employee_db = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.id == VacationRequest.Employee_id).first()
    Employee_Total_Vacation = Employee_db.get_total_vacation()

    if Employee_Total_Vacation < VacationRequest.RequestedValue :
        return jsonify({"status": "failed", "message":"کاربر مورد نظر اعتبار کافی برای درخواست مرخصیی ندارد لطف درخواست را رد کنید"}), 400


    # update employee vacation total
    Employee_db.set_vacation_total_value(VacationRequest.RequestedValue)

    AdminAcccess = AdminModel.VacationRequestHandler.query \
        .filter(AdminModel.VacationRequestHandler.UserId == UserDB.id) \
            .filter(AdminModel.VacationRequestHandler.WorkPositionId == VacationRequest.WorkPositionId)\
                .first()


    admin_role = AuthModel.Role.query.filter(AuthModel.Role.RoleName == "admin").first().id
    # check if admin was doing request pass
    if UserDB.UserRole != admin_role:
        if not AdminAcccess:
            return jsonify({"status": "failed", "message":"ادمین گرامی شما مجوز دسترسی و اعمال عملیات برای درخواست های این گروه را ندارید"}), 400

    if op == "reject":
        VacationRequest.VacationStatus = "رد شد"
    elif op == "approve":
        VacationRequest.VacationStatus = "تایید شد"

    VacationRequest.ApprovedBy = session.get("account-id")

    db.session.add(VacationRequest)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({"status": "failed", "message":"خطایی هنگام ذخیره رخ داد"}), 400
    else:
        return jsonify({"status": "success", "message":"عملیات با موفقیت انجام شد"}), 200

