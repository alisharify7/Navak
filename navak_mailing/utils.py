from flask import jsonify

import navak_mailing.models as MessageModel
from navak.utils import validate_date
from navak.utils import convert_dt2_khayyam, convert_kh2_datetimeD

def invalid_json_request(message="", status="failed", code=401):
    """
        this view take a message and status code for json error response
    """
    dt = {
        "status": status,
        "message": message,
    }
    return jsonify(dt), code


def json_data_request(message="", status="success", data=[], code=200, paginate=[], total_pagination=0):
    dt = {
        "status": status,
        "message": message,
        "data": data,
        "pagination": paginate,
        "total_pagination": total_pagination
    }
    return jsonify(dt), code


def load_user_received_messages(user_id: int, page: int, per_page: int):
    """
        this function take user id and return a flask-sqlalchemy
        pagination object from received messages of that user

        :params: user_id=int, page=int, per_page=int
        :return: flask-sqlalchemy:paginate
    """
    return MessageModel.Mailing.query.filter(MessageModel.Mailing.To == user_id) \
        .order_by(MessageModel.Mailing.id.desc()) \
        .paginate(page=page, per_page=per_page)


def load_user_sends_messages(user_id: int, page: int, per_page: int):
    """
        this function take user id and return a flask-sqlalchemy
        pagination object from received messages of that user

        :params: user_id=int, page=int, per_page=int
        :return: flask-sqlalchemy:paginate
    """
    return MessageModel.Mailing.query.filter(MessageModel.Mailing.From == user_id) \
        .order_by(MessageModel.Mailing.id.desc()) \
        .paginate(page=page, per_page=per_page)


def search_in_mails(filter_db, SearchOption, SeachBox, user_db):
    """
        this function search in users mail and return data with applied filters

        :params: filter_db=flask-sqlalchemy, SearchOption=string, SeachBox=string, user_db:flask-sqlalchemy.data
        :return: flask-sqlalchemy.data

        error_return: tuple

    """

    if SearchOption == "MailNumber":
        try:
            SeachBox = int(SeachBox)
        except ValueError:
            return "شماره نامه وارد شده دارای فرمت نادرست می باشد",

        message = MessageModel.Mailing.query.filter(filter_db == user_db.id) \
            .filter(MessageModel.Mailing.id == SeachBox).all()

    elif SearchOption == "MailDate":
        if not (SeachBox := validate_date(SeachBox)):
            return "تاریخ وارد شده دارای فرمت مناسب نمی باشد",

        message = MessageModel.Mailing.query.filter(filter_db == user_db.id) \
            .filter(MessageModel.Mailing.MailDate == SeachBox).all()

    elif SearchOption == "MailText":
        message = MessageModel.Mailing.query.filter(filter_db == user_db.id) \
            .filter(MessageModel.Mailing.MailCaption.ilike(f"%{SeachBox}%")).all()

    return message if message else False
