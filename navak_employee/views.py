import datetime
import os.path

import khayyam
from flask import (
    flash,
    request,
    jsonify,
    redirect,
    render_template,
    send_from_directory,

)
from navak.utils import convert_dt2_khayyam, convert_kh2_datetimeD
from navak.extensions import db
from navak_employee import employee
import navak_employee.forms as EmployeeForms
import navak_employee.models as EmployeeModel
from navak_auth.utils import employee_login_required
from navak_employee.utils import Pars_Time_Request_Vacation
from navak.utils import validate_date
from navak_config.config import EMPLOYEE_PRIVATE_STATIC


@employee.route("/private/static/<path:path>")
@employee_login_required
def private_static(employee_db,path):
    if os.path.exists(EMPLOYEE_PRIVATE_STATIC / path):
        return send_from_directory(EMPLOYEE_PRIVATE_STATIC, path)
    else:
        return "File Not Found !", 404


@employee.route("/")
@employee_login_required
def index_view(employee_db):
    content = {
        "page": "dashboard"
    }

    content["ContractType"] = employee_db.ContractType
    content["StartContract"] = employee_db.StartContract
    content["EndContract"] = employee_db.EndContract
    content["VacationLeft"] = employee_db.get_total_vacation()
    content["DayPass"] = (khayyam.JalaliDate.today() - khayyam.JalaliDate(day=employee_db.StartContract.day, year=employee_db.StartContract.year, month=employee_db.StartContract.month)).days
    content["DayRemain"] = (khayyam.JalaliDate(day=employee_db.EndContract.day, year=employee_db.EndContract.year, month=employee_db.EndContract.month) - khayyam.JalaliDate.today()).days

    return render_template("employee/index.html", content=content)


@employee.route("/vacation/", methods=["GET"])
@employee_login_required
def vacation_request_get(employee_db):
    content = {
        "page": "vacation"
    }

    approved_page = request.args.get(key='approve', default=1, type=int)
    waited_page = request.args.get(key='waited', default=1, type=int)
    rejected_page = request.args.get(key='rejected', default=1, type=int)

    form = EmployeeForms.VacationRequest()

    approve_vacations = EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.Employee_id == employee_db.id)\
        .filter(EmployeeModel.VacationRequest.VacationStatus == "تایید شد").order_by(EmployeeModel.VacationRequest.id.desc()).paginate(per_page=6, page=approved_page)

    waited_vacations = EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.Employee_id == employee_db.id)\
        .filter(EmployeeModel.VacationRequest.VacationStatus == "در انتظار تایید").order_by(EmployeeModel.VacationRequest.id.desc()).paginate(per_page=6, page=waited_page)

    rejected_vacations = EmployeeModel.VacationRequest.query.filter(EmployeeModel.VacationRequest.Employee_id == employee_db.id)\
        .filter(EmployeeModel.VacationRequest.VacationStatus == "رد شد").order_by(EmployeeModel.VacationRequest.id.desc()).paginate(per_page=6, page=rejected_page)

    content["approved"] = approve_vacations
    content["rejected"] = rejected_vacations
    content["waited"] = waited_vacations
    content["waited_current_page"] = waited_page
    content["approve_current_page"] = approved_page
    content["rejected_current_page"] = rejected_page

    return render_template("employee/Vacation/VacationRequest.html", content=content, form=form)


@employee.route("/vacation/", methods=["POST"])
@employee_login_required
def vacation_request_post(employee_db):
    content = {
        "page": "vacation"
    }
    form = EmployeeForms.VacationRequest(request.form)
    if not form.validate():
        flash("برخی موارد مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        employee_vacation_left = employee_db.get_total_vacation()

        employee_requested_value = Pars_Time_Request_Vacation(form.RequestTarget.data)
        if not employee_requested_value:
            flash("مقدار درخواستی به درستی وارد نشده است" , "danger")
            return redirect(request.referrer)

        requested_date = validate_date(form.RequestTargetDate.data)
        if not requested_date:
            flash("تاریخ به درستی وارد نشده است", "danger")
            return redirect(request.referrer)

        # check employee have enough vacation to request
        if employee_vacation_left-employee_requested_value < 0:
            flash("کارمند گرامی شما مقدار کافی برای درخواست مرخصی ندارید", "danger")
            return redirect(request.referrer)


        # create a new vacation request
        new_vacation = EmployeeModel.VacationRequest()
        new_vacation.Employee_id = employee_db.id
        new_vacation.RequestedValue = employee_requested_value
        new_vacation.WorkPositionId = employee_db.WorkPosition
        new_vacation.RequestedDate = convert_kh2_datetimeD(requested_date)
        new_vacation.RequestTitle = form.RequestTitle.data
        new_vacation.RequestCaption = form.RequestBody.data
        new_vacation.set_public_key()
        db.session.add(new_vacation)
        try:
            db.session.commit()
        except:
            flash("خطایی هنگام ذخیره سازی رخ داد", "danger")
            db.session.rollback()
        else:
            flash("درخواست در صف انتظار قرار گرفت", "success")

        return redirect(request.referrer)



@employee.route("/work/report/")
@employee_login_required
def work_report_get(employee_db):
    content = {
        "page": "workreport"
    }
    page = request.args.get(key="page", type=int, default=1)

    content["Reports"] = EmployeeModel.WorkReport.query.filter(EmployeeModel.WorkReport.EmployeeId == employee_db.id).order_by(EmployeeModel.WorkReport.id.desc()) \
                .paginate(page=page, per_page=15)

    content["current_page"] = page
    form = EmployeeForms.WorkReport()
    return render_template("employee/WorkReport/WorkReport.html", content=content, form=form)


@employee.route("/work/report/", methods=["POST"])
@employee_login_required
def work_report_post(employee_db):
    """
        this view take a work report via post method
        and regiter it for employee
    """
    content = {
        "page": "workreport"
    }
    form = EmployeeForms.WorkReport()

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده است" ,"danger")
        return redirect(request.referrer)

    if form.validate():
        today_report = EmployeeModel.WorkReport.query.filter(EmployeeModel.WorkReport.EmployeeId == employee_db.id)\
            .filter(EmployeeModel.WorkReport.ReportDate == khayyam.JalaliDate.today())\
                .first()

        if today_report:
            flash("کارمند گرامی شما برای امروز، گزارش کار خود را نوشته اید" ,"danger")
            return redirect(request.referrer)

        else:
            new_reporrt = EmployeeModel.WorkReport()
            new_reporrt.EmployeeId = employee_db.id
            new_reporrt.ReportBody = form.ReportWorkBody.data

            db.session.add(new_reporrt)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash("برخی موارد مقدار دهی اولیه نشده است"  ,"danger")
            else:
                flash("عملیات با موفقیت انجام شد" ,"success")

            return redirect(request.referrer)




@employee.route("/_get/report/work/30/", methods=["POST"])
@employee_login_required
def report_work_api(employee_db):
    """
    this api view return user last month work report in json
    """
    date_target = datetime.date.today() + datetime.timedelta(days = -31)

    data = [[], []]
    while date_target < datetime.date.today():
        date_target += datetime.timedelta(days=1)
        report = EmployeeModel.WorkReport.query.filter(EmployeeModel.WorkReport.EmployeeId == employee_db.id)\
            .filter(EmployeeModel.WorkReport.ReportDate == date_target).first()
        if report:
            data[0].append(str(convert_dt2_khayyam(date_target)))
            data[1].append(1)
        else:
            data[0].append(str(convert_dt2_khayyam(date_target)))
            data[1].append(0)

    return jsonify({"dates": data[0], "datas": data[1]}), 200




