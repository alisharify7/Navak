import navak_admin.models as AdminModel
from navak_config.utils import load_education, load_work_position, load_roles


def get_all_education():
    """
        this function return all education degrees in tuple format
        for wtforms
    :return: tuple
    """
    education = load_education()
    data = []
    for each in education:
        data.append((each["name"], each["name"],))

    return data


def get_all_work_position():
    """
        this function return all workPositions in tuple format
        for wtforms
    :return: tuple
    """
    education = load_work_position()
    data = []
    for each in education:
        data.append((each["name"], each["name"],))

    return data


def get_all_roles():
    """
        this function return all roles in tuple format
        for wtforms
    :return: tuple
    """
    education = load_roles()
    data = []
    for each in education:
        data.append((each["role-fa"], each["role-fa"],))

    return data


def searchInProjectFunc(filter_s: str, data: str):
    """
        this function take a filter and data
        and search in project for that data with that filter
    """
    if filter_s == "StartDate":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectStartDate == data).all()
    elif filter_s == "EndDate":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectEndDate == data).all()
    elif filter_s == "Handler":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectHandler == data).all()
    elif filter_s == "Amount":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectAmount == data).all()
    elif filter_s == "WordINText":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectDescription.ilike(f"%{data}%")).all()
    else:
        # elif filter_s == "ProjectStatus":
        return AdminModel.Project.query.filter(AdminModel.Project.ProjectStatus == data).all()
