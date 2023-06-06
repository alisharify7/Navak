import os.path
import pathlib
import uuid

from flask import request, session, abort, flash, redirect, render_template, send_from_directory, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename


import navak_auth.models as UserModel
import navak_config.config as config
import navak_mailing.forms as MailForms
import navak_mailing.models as MessageModel
from navak.utils import convert_dt2_khayyam, convert_kh2_datetimeD
from navak.extensions import db
from navak_auth.utils import basic_login_required, LoadUserObject
from navak_mailing import message
from navak_mailing.utils import invalid_json_request, json_data_request


@message.route("/setup/")
def setup():
    for each in range(75):
        mail = MessageModel.Mailing()
        mail.set_public_key()
        mail.From = 26
        mail.To = 27
        mail.MailTitle = f"پیام شماره - {each}"
        mail.MailCaption = f"پیام شماره - {each}"
        mail.MailAttach = f"پیام شماره - {each}"
        db.session.add(mail)
        db.session.commit()
        print("added")

    return "Ok"


@message.route("/", methods=["POST"])
@basic_login_required
def get_all_messages():
    """
        this view take only json request and return index message data for user
    """
    if not request.is_json:
        return invalid_json_request(message="This Endpoint Only Accept Json Request", status=415)

    if request.is_json:
        if not (user_db := LoadUserObject(session.get("account-id"))):
            return invalid_json_request(message="Invalid Credential", status=401)

        data = request.get_json()

        if not (page := data.get("page", None)):
            return invalid_json_request(message="Missing Page key in data", status=400)

        if not str(page).isdigit():
            return invalid_json_request(message="Invalid key data type", status=400)

        page = int(page)

        messages = MessageModel.Mailing.query.filter(MessageModel.Mailing.To == user_db.id) \
            .order_by(MessageModel.Mailing.id.desc()) \
            .paginate(page=page, per_page=10)

        data = []
        for each in messages:
            temp = {}
            temp["MailTitle"] = each.MailTitle
            temp["MailTime"] = f"{convert_dt2_khayyam(each.MailTime.date())} {each.MailTime.time()}"
            temp["From"] = LoadUserObject(each.From).FullName
            temp["To"] = LoadUserObject(each.To).FullName
            temp["MailAttach"] = 0 if each.MailAttach else 1
            temp["MailKey"] = each.PublicKey
            temp["IsWatched"] = each.is_watched
            data.append(temp)

        pagination = []
        for each in messages.iter_pages(right_edge=1, left_edge=1, right_current=1, left_current=1):
            if each:
                pagination.append(each)

        return json_data_request(message="All User Received Messages",
                                 status="success",
                                 data=data,
                                 code=200,
                                 paginate=pagination,
                                 total_pagination=messages.pages,
                                 )


@message.route("/send/", methods=["POST"])
@basic_login_required
def mail_send_message_post():
    """
        this view take a Mail and send it for user
    """
    form = MailForms.SendMailForm(request.form)

    if not form.validate():
        flash("برخی موارد مقدار دهی نشده اند", "danger")
        return redirect(request.referrer)

    if form.validate():

        # check user target tag is ok
        # save attach file and commit change to db
        mail = MessageModel.Mailing()
        mail.set_public_key()

        if not (user_db := LoadUserObject(session.get("account-id"))):
            session.clear()
            abort(401)
        mail.From = user_db.id

        # get user target by usertag
        if not (user_target_db := UserModel.User.query.filter(UserModel.User.Usertag == form.MailTarget.data).first()):
            flash("کاربری با شناسه کاربری وارد شده یافت نشد ", "danger")
            return redirect(request.referrer)
        mail.To = user_target_db.id

        if mail.To == mail.From:
            flash("گیرنده و فرستنده نامه نمی تواند یک شخص باشد ", "danger")
            return redirect(request.referrer)

        if file := request.files.get("MailAttach"):
            if pathlib.Path(file.filename).suffix.lower() not in [".pdf"]:
                flash("فرمت فایل انتخاب شده پشتیبانی نمی شود", "danger")
                return redirect(request.referrer)

            mail.MailAttach = str(uuid.uuid4()) + secure_filename(file.filename[-50:])

        mail.MailTitle = form.MailTitle.data
        mail.MailCaption = form.MailCaption.data

        if file:
            try:
                file.save(config.ATTACH_FILES_DIR / mail.MailAttach)
            except Exception as e:
                if os.path.exists(config.ATTACH_FILES_DIR / mail.MailAttach):
                    os.remove(config.ATTACH_FILES_DIR / mail.MailAttach)

                flash("خطایی هنگام ذخیره فایل رخ داد", "danger")
                return redirect(request.referrer)

        db.session.add(mail)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            if file:
                if os.path.exists(config.ATTACH_FILES_DIR / mail.MailAttach):
                    os.remove(config.ATTACH_FILES_DIR / mail.MailAttach)

            flash("خطایی هنگام ارسال رخ داد", "danger")
            return redirect(request.referrer)
        else:
            flash("پیام با موفقیت برای گیرنده ارسال شد", "success")
            return redirect(request.referrer)


@message.route("/show/<uuid:message_key>")
@basic_login_required
def show_message(message_key):
    """
        this view take a message key and show message full info to user
        only show to users that is sender of this message or receiver of it
    """
    content = {}
    message_key = str(message_key)

    message_db = MessageModel.Mailing.query.filter(MessageModel.Mailing.PublicKey == message_key).first()
    if not message_db:
        abort(401)
    if session.get("account-id") not in [message_db.From, message_db.To]:
        abort(401)

    # replace georgian time with jalali time
    message_db.MailDate = convert_dt2_khayyam(message_db.MailDate)

    content["referrer"] = request.referrer
    content["message"] = message_db
    return render_template("mailing/show_mail.html", content=content)


@message.route("/get/attach/<uuid:mail_key>/")
@basic_login_required
def send_mail_attach(mail_key):
    """
        this view take an mail request and check if user have access to that mail return mail attach file
    """
    mail_key = str(mail_key)

    message_db = MessageModel.Mailing.query.filter(MessageModel.Mailing.PublicKey == mail_key).first()
    if not message_db:
        abort(401)

    if session.get("account-id") not in [message_db.From, message_db.To]:
        abort(401)

    if not message_db or not message_db.MailAttach:
        abort(401)

    return send_from_directory(config.ATTACH_FILES_DIR, message_db.MailAttach, as_attachment=True)


@message.route("/_get/user/signature/<int:user_id>")
@basic_login_required
def get_user_signature(user_id):
    """
        this view return user signature that it's id pass by get params
        its check user that request this image have at least a message from this user
    """
    # Get user that it's id passed by get params object from db
    user_requested = LoadUserObject(session.get("account-id")).id

    message_db = MessageModel.Mailing.query.filter(MessageModel.Mailing.From == user_id).filter(
        MessageModel.Mailing.To == user_requested).first()

    if message_db or user_id == user_requested:
        return send_from_directory(config.USER_SIGNATURE_DIR, LoadUserObject(user_id).UserSignature)
    else:
        abort(401)


@message.route("/_get/new/messages/", methods=["POST"])
@basic_login_required
def new_messages():
    """
        this view return user un watched messages count
    """
    messages = len(MessageModel.Mailing.query.filter(MessageModel.Mailing.To == session.get("account-id")).filter(MessageModel.Mailing.is_watched == False).all())
    return jsonify({"status":"success", "UnseenMessages": messages}), 200


@message.route("/_set/seen/messages/", methods=["POST"])
@basic_login_required
def set_seen_message():
    """
        this view change user message seen status

    :params: key: publickey:mail object
    """
    if not(key := request.form.get("key")):
        return jsonify({"status": "failed", "message":"Missing key"}), 400

    message_db = MessageModel.Mailing.query.filter(MessageModel.Mailing.PublicKey == key)\
        .filter(MessageModel.Mailing.To == session.get("account-id"))\
        .first_or_404()

    if not message_db.is_watched:
        message_db.is_watched = True
        db.session.add(message_db)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        else:
            return jsonify({"status":"success","message":"message read by user"}), 200
    else:
            return jsonify({"status":"success","message":"message was saw by user"}), 200
