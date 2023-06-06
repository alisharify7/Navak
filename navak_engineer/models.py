import datetime

from navak.extensions import db
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime



class ProjectComments(db.Model):
    __tablename__ = "navak_project_comments"

    id = Column(Integer(), primary_key=True)
    Comment = Column(String(1024), nullable=False)
    CreatedTime = Column(DateTime(), default=datetime.datetime.now)
    project_id = Column(Integer(), ForeignKey("navak_project.id"))
    engineer_id = Column(Integer(), ForeignKey("navak_users.id"))