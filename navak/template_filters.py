import datetime
import json

import khayyam

import navak_config.config as config
import navak_store.models as StroeModel
from navak import app
from navak_auth import models as UserModel
from navak_auth.utils import LoadUserObject
from navak_employee import models as EmployeeModel

import navak_admin.models as AdminModel
from navak.utils import convert_dt2_khayyam


@app.template_filter("RoleName")
def RoleName(Role_id: int):
    """
        this template filter take a role id
        and return name of that role id
    :param Role id:
    :return: Role Name
    """
    if not (RoleDB := UserModel.Role.query.filter(UserModel.Role.id == Role_id).first()):
        return "NULL"
    else:
        print("شیسس")
        return RoleDB.RoleDescription


@app.template_filter("WorkPositionName")
def WorkPositionName(WorkPosition_id: int):
    """
        this template filter take a WorkPosition id
        and return name of that WorkPositionName id
    :param WorkPositionName id:
    :return: WorkPositionName
    """
    if not (workpositon_db := EmployeeModel.WorkPosition.query.filter(
            EmployeeModel.WorkPosition.id == WorkPosition_id).first()):
        return "NULL"
    else:
        return workpositon_db.Name


@app.template_filter("HaveSignature")
def HaveSignature(user_id: int):
    """
    :param user id:
    :return: True if user have signature otherwise False
    """
    if not (user_db := UserModel.User.query.filter(UserModel.User.id == user_id).first()):
        return False

    if user_db.UserSignature:
        return True
    return False

@app.template_filter("UserName")
def UserName(user_id: int) -> str:
    """
        this filter take a user id and return user name from db
    :param user id:
    :return: user Name
    """
    if not (user_db := LoadUserObject(user_id)):
        return "NULL"
    else:
        return user_db.FullName


@app.template_filter("EmployeeName")
def EmployeeName(employee_id: int) -> str:
    """
        this filter take a employee id and return employee name from db
    :param employee id:
    :return: employee name
    """

    employee_db = EmployeeModel.Employee.query.filter(EmployeeModel.Employee.id == employee_id).first()
    if not employee_db:
        return "None"
    else:
        return employee_db.FirstName + ' ' + employee_db.LastName


@app.template_filter("WorkPositionName")
def WorkPositionName(WorkPosition: int) -> str:
    """
        this template filter take a work position and return work Position name
    """

    workposition_db = EmployeeModel.WorkPosition.query.filter(EmployeeModel.WorkPosition.id == WorkPosition).first()
    if not workposition_db:
        return "None"
    else:
        return workposition_db.Name


@app.template_filter("ProjectProductList")
def ProjectProductList(data):
    """
        this template filter take product of project in format of
        {"b682c7a3-ad98-4275-8d8b-fc07a4fae208": 1123, "107480e2-e1f3-44e1-a7c9-d401bf5b540b": 1123123, "67eb72e1-ecbc-480f-b359-154a1501352f": 1123213}
        { productkey:number}
        and return a list in format of
        [ {name of product: number of it} ]

    """
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        return ["ERROR"]

    dt = []
    for each in data:
        db_query = StroeModel.Product.query.filter(StroeModel.Product.PublicKey == each).first()
        if db_query:
            dt.append({"id": db_query.id, "ProductName": db_query.ProductName, "count": data[each]})

    return dt



@app.template_filter("GET_PROJECT_TYPE")
def GET_PROJECT_TYPE(project_typename:str):
    """
        this filter take a string
        and search it in PROJECT_TYPE and if it found it return
        Persian of it

    PROJECT_TYPE = [
        ("research", "تحقیقاتی"),
        ("commercial", "تجاری"),
        ("military", "نظامی")
    ]

    """
    for each in config.PROJECT_TYPE:
        if project_typename in each:
            return each[-1]

    return project_typename


@app.template_filter("GET_PROJECT_STATUS")
def GET_PROJECT_STATUS(project_status: str):
    """
        this filter take a string
        and search it in PROJECT_STATUS and if it found it return
        Persian of it

        PROJECT_STATUS_TYPE = [
            ("continued", "در حال انجام"),
            ("stopped", "متوقف شده"),
            ("ended", "اتمام یافته")
        ]

    """
    for each in config.PROJECT_STATUS_TYPE:
        if project_status in each:
            return each[-1]

    return project_status


@app.template_filter("HaveSignature")
def HaveSignature(user_id: int) -> bool:
    """
        this template filter check user have signature or not
    """
    if not (user_db := LoadUserObject(user_id)):
        print("NOt")
        return False
    if user_db.UserSignature:
        print("Yes")
        return True
    else:
        print("Not")
        return False


@app.template_filter("isVacationHandler")
def isVacationHandler(userID: int) -> bool:
    result = AdminModel.VacationRequestHandler.query.filter(AdminModel.VacationRequestHandler.UserId == userID).first()
    return True if result else False

@app.template_filter("convert_dt2_khayyam")
def convert_dt2_khayyam_filter(date: datetime.datetime) -> khayyam.JalaliDatetime:
    """
        this template filter  take a datetime object (georgian) and convert it to khayyam object (jalali)
    """
    return convert_dt2_khayyam(date)


# for pycharm optimize import just temporary do this
ok = "Template filter's are Loaded Successfully :)"
