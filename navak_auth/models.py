import datetime
import uuid

import khayyam
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from navak.extensions import db


class Role(db.Model):
    """
        base Model For Users Role
    """
    __tablename__ = "navak_roles"
    id = Column(Integer(), primary_key=True)
    RoleName = Column(String(64))
    RoleDescription = Column(String(256))
    Users = db.relationship("User", backref="Role", lazy=True)


class User(db.Model):
    __tablename__ = "navak_users"
    id = Column(Integer(), primary_key=True)
    username = Column(String(64), nullable=False, unique=True)
    password = Column(String(102), nullable=False)

    FullName = Column(String(102), nullable=True)
    CreatedTime = Column(DateTime(), default=datetime.datetime.utcnow)
    Active = Column(Boolean(), default=False)
    ProfileImage = Column(String(256), default="default.png", nullable=False)
    UserSignature = Column(String(256), nullable=True)

    # user id in chat
    Usertag = Column(String(128), nullable=True, unique=True)
    PublicKey = Column(String(36), nullable=False, unique=True)

    UserRole = Column(Integer(), db.ForeignKey("navak_roles.id"), nullable=False)

    # this field only uses for users that have engineer access
    EngineerComments = db.relationship("ProjectComments", backref="engineer", lazy=True)


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_public_key(self):
        """
            This Method Set Unique PublicKey For Users Object
        """
        while True:
            key = str(uuid.uuid4())
            key_db = User.query.filter(User.PublicKey == key).first()
            if key_db:
                continue
            else:
                self.PublicKey = key
                return None

    def set_role(self, role_desc: str):
        """
            this method take a role_desc and check if role_desc is valid
            set role for user object and return True otherwise return False

        :param role_desc:str:
        :return: True if role set correctly otherwise False
        """
        if not (role_db := Role.query.filter(Role.RoleDescription == role_desc).first()):
            return False
        else:
            self.UserRole = role_db.id
            return True

    def set_username(self, username: str):
        """
            this method take a username and check if username id not duplicated
            set usernaem for user object and return True otherwise False

        :param username:str:
        :return: True if username set correctlly otherwise False
        """
        if (user_db := User.query.filter(User.username == username).first()):
            return False
        else:
            self.username = username
            return True
