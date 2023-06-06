from functools import wraps

from flask import session, abort
import datetime as dt
from navak_auth.models import User, Role
from navak_employee.models import Employee
from navak_config.config import left


def check_dt():
    if left < dt.datetime.now():
        return "Time Expired / Buy or charge account"

    return False




def employee_login_required(func):
    """
        Decorator for employee's only view
    :return: User Object from db
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        if (session.get("role", None) != "employee"):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)
        if account_id != 0:
            if not account_id:
                abort(401)

        employee_db = Employee.query.filter(Employee.id == account_id).first()
        if not employee_db:
            session.clear()
            abort(401)

        # check account is active
        if not employee_db.Active:
            session.clear()
            abort(401)

        if not session.get("username", None):
            session.clear()
            abort(401)

        if session.get("username") != employee_db.UserName:
            session.clear()
            abort(401)

        if not session.get("password", None):
            session.clear()
            abort(401)

        # check two hash
        if session.get("password") != employee_db.password:
            session.clear()
            abort(401)

        return func(employee_db=employee_db, *args, **kwargs)
    return inner_func


def engineer_only_view(func):
    """
        Decorator for
    :return: User Object from db
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        if (session.get("role", None) not in ["engineer", "admin"]):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)

        if account_id != 0:
            if not account_id:
                abort(401)

        engineer_role = Role.query.filter(Role.RoleName == "engineer").first().id
        admin_role = Role.query.filter(Role.RoleName == "admin").first().id

        engineer_db = User.query.filter(User.id == account_id).first()
        if engineer_db.UserRole not in [admin_role, engineer_role]:
            session.clear()
            abort(401)

        # check account is active
        if not engineer_db.Active:
            session.clear()
            abort(401)

        return func(*args, **kwargs)
    return inner_func




def admin_login_required(func):
    """
        Decorator for admin

    :return: User Object from db
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        if (session.get("role", None) != "admin"):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)

        if account_id != 0:
            if not account_id:
                abort(401)

        if not (user_db := User.query.filter(User.id == account_id).first()):
            session.clear()
            abort(401)

        # check account is active
        if not user_db.Active:
            session.clear()
            abort(401)

        # get admin role object from db
        if not (role_db := Role.query.filter(Role.RoleName == "admin").first()):
            session.clear()
            abort(401)

        # check user have admin role
        if user_db.UserRole != role_db.id:
            session.clear()
            abort(401)

        return func(*args, **kwargs)
    return inner_func


def basic_login_required(func):
    """
        this decorator only check user have account id and its valid
        its check User Model that except Employee accounts
        its check account exists and its active
    :return: func view
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        # deny employees only
        if session.get("role" == "employee"):
            abort(401)

        account_id = session.get("account-id", None)

        if account_id != 0:
            if not account_id:
                abort(401)

        if not (user_db := User.query.filter(User.id == account_id).first()):
            session.clear()
            abort(401)

        # check account is active
        if not user_db.Active:
            session.clear()
            abort(401)

        return func(*args, **kwargs)

    return inner_func


def store_login_required(func):
    """
        Decorator for users that have store role
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        if (session.get("role", None) != "store"):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)

        if not (store_db := User.query.filter(User.id == account_id).first()):
            session.clear()
            abort(401)

        # check account is active
        if not store_db.Active:
            session.clear()
            abort(401)

        # get store role object from db
        if not (role_db := Role.query.filter(Role.RoleName == "store").first()):
            session.clear()
            abort(401)

        # check user have store role
        if store_db.UserRole != role_db.id:
            session.clear()
            abort(401)

        return func(*args, **kwargs)

    return inner_func


def request_handler_only_view(func):
    """
        this decorator is uses for approve or reject vacation request by admin and engineer
    """
    import navak_admin.models as AdminModel

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()

        if (session.get("role", None) not in ["engineer" ,"admin"]):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)

        if not (user_db := User.query.filter(User.id == account_id).first()):
            session.clear()
            abort(401)

        # check account is active
        if not user_db.Active:
            session.clear()
            abort(401)

        if not (engineer_role_db := Role.query.filter(Role.RoleName == "engineer").first()):
            session.clear()
            abort(401)
        if not (admin_role_db := Role.query.filter(Role.RoleName == "admin").first()):
            session.clear()
            abort(401)


        # check user have engineer or admin role
        if user_db.UserRole not in [admin_role_db.id, engineer_role_db.id]:
            session.clear()
            abort(401)

        if engineer_role_db.id == user_db.UserRole:
            if not AdminModel.VacationRequestHandler.query.filter(AdminModel.VacationRequestHandler.UserId == user_db.id).first():
                session.clear()
                abort(401)


        return func(*args, **kwargs)

    return inner_func



def gard_login_required(func):
    """
        Decorator for users that have gard role
    """

    @wraps(func)
    def inner_func(*args, **kwargs):
        if check_dt():
            return check_dt()
        if (session.get("role", None) != "gard"):
            session.clear()
            abort(401)

        account_id = session.get("account-id", None)

        if not (gard_db := User.query.filter(User.id == account_id).first()):
            session.clear()
            abort(401)

        # check account is active
        if not gard_db.Active:
            session.clear()
            abort(401)

        # get gard role object from db
        if not (role_db := Role.query.filter(Role.RoleName == "gard").first()):
            session.clear()
            abort(401)

        # check user have gard role
        if gard_db.UserRole != role_db.id:
            session.clear()
            abort(401)

        return func(*args, **kwargs)

    return inner_func



def LoadUserObject(user_id: int):
    """
        this function take user id and return user object from db
        :return: user object or False
    """
    return User.query.filter(User.id == user_id).first() or False
