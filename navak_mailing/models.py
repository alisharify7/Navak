import datetime
import uuid

from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean

from navak.extensions import db


class Mailing(db.Model):
    """
        base Model For mailing in system
    """
    __tablename__ = "navak_mailes"
    id = Column(Integer(), primary_key=True)

    MailTitle = Column(String(128), nullable=True)
    MailCaption = Column(String(4096), nullable=True)
    MailTime = Column(DateTime(), default=datetime.datetime.now)

    From = Column(Integer(), db.ForeignKey("navak_users.id"), nullable=False)
    To = Column(Integer(), db.ForeignKey("navak_users.id"), nullable=False)

    PublicKey = Column(String(36), nullable=False)

    MailAttach = Column(String(512), nullable=True, unique=False)
    MailDate = Column(Date(), nullable=True, default=datetime.datetime.now)
    is_watched = Column(Boolean(), nullable=False, default=False)
    def __str__(self):
        return f"{self.id}-{self.MailTitle[:15]}"

    def set_public_key(self):
        while True:
            key = str(uuid.uuid4())
            key_db = Mailing.query.filter(Mailing.PublicKey == key).first()
            if not key_db:
                self.PublicKey = key
                break
            else:
                continue
