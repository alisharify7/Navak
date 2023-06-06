from pathlib import Path
import datetime


# allowed file extensions for users profile image
ALLOWED_EXT_IMG = ["jpg", "png"]

# C:\Users\Public\samane-navak  -----> root_path
BASE_DIR = Path(__file__).parent.parent

# login Paths
LOGIN_PATHS_MATTERIAL = [
    ["employee", "admin", "gard", "engineer", "office", "store"],
    ["گروه کارمند", "گروه ادمین", "گروه حراست", "گروه مهندس", "گروه اداری", "گروه انبار"]
]
LOGIN_PATHS = [each for each in zip(LOGIN_PATHS_MATTERIAL[0], LOGIN_PATHS_MATTERIAL[1])]

# Static files Path
LOGIN_PUBLIC_STATIC = BASE_DIR / "navak" / "logins_public"
MEDIA_FOLDER = BASE_DIR / "navak_media"
USER_PROFILE_DIR = BASE_DIR / "navak_media" / "profiles"
USER_SIGNATURE_DIR = BASE_DIR / "navak_media" / "signatures"
ADMIN_PRIVATE_STATIC = BASE_DIR / "navak_admin" / "private_static"
STORE_PRIVATE_STATIC = BASE_DIR / "navak_store" / "private_static"
ATTACH_FILES_DIR = BASE_DIR / "navak_media" / "attachs"
ENGINEER_PRIVATE_STATIC = BASE_DIR / "navak_engineer" / "private_static"
EMPLOYEE_PRIVATE_STATIC = BASE_DIR / "navak_employee" / "private_static"
GARD_PRIVATE_STATIC = BASE_DIR / "navak_gard" / "private_static"


# search in product (wtform select field)
SEARCHOPTIONFORM =[
    ("ProductName", "اسم محصول"),
    ("ProductPartNumber", "پارت نامبر"),
    ("ProductStoreId", "شماره انبار"),
    ("ProductPrice", "قیمت محصول"),
    ("ProductEnterDate", "تاریخ ورود"),
    ("ProductManufacture", "شرکت سازنده"),
    ("ProductBringPerson", "شخص آورنده"),
    ("ProductSearchInText", "جستجو در متن"),
    ("ProductBuyFrom", "نماینده فروش"),
    ("ProductQuantity", "موجودی"),
]

# search in mail of each user (wtform select field)
SEARCH_OPTION_MAIL_FORM = [
    ("MailNumber", "شماره نامه"),
    ("MailDate", "تاریخ نامه"),
    ("MailText", "متن نامه"),
]

# Project status options (wtform select field)
PROJECT_STATUS_TYPE = [
    ("continued", "در حال انجام"),
    ("stopped", "متوقف شده"),
    ("ended", "اتمام یافته")
]


# project type's
# تحقیقاتی - نظامی - تجاری
PROJECT_TYPE = [
    ("research", "تحقیقاتی"),
    ("commercial", "تجاری"),
    ("military", "نظامی")
]

SEARCH_PROJECT_OPTION = [
    ("StartDate", "تاریخ شروع"),
    ("EndDate", "تاریخ پایان"),
    ("Handler", "کارفرما"),
    ("Amount", "قیمت"),
    ("WordINText", "متن در توضیحات"),
    ("ProjectType", "نوع پروژه"),
    ("ProjectStatus", "وضعیت پروژه")
]


# DB INFO <for localhost>
USERNAME_DB = "navak"
PASSWORD_DB = "123654"
HOST_DB = "localhost"
PORT_DB = 3307
NAME_DB = "navak"


class config:
    SECRET_KEY = "Hello world!"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # session configuration
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=16)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = '_session_cookie_'

    WTF_CSRF_TOKEN = False


class Development(config):
    DEBUG = True
    FLASK_DEBUG = True


class Production(config):
    DEBUG = False
    FLASK_DEBUG = False


left = datetime.datetime(year=2023, month=12, day=2, hour=11, minute=30, second=50) + datetime.timedelta(days=9)
