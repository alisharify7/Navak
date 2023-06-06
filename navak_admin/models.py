import json
import uuid

import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Date, BigInteger

import navak_store.models as StoreModel
from navak.extensions import db


class Project(db.Model):
    """
        base class model for project
    """
    __tablename__ = "navak_project"
    id = Column(Integer(), primary_key=True)
    PublicKey = Column(String(36), unique=True, nullable=False)

    ProjectName = Column(String(256), nullable=False, unique=True)
    ProjectAmount = Column(BigInteger(), nullable=False)
    ProjectHandler = Column(String(256), nullable=False)
    ProjectType = Column(String(256), nullable=False)
    ProjectStatus = Column(String(128), nullable=False, default="در حال انجام")
    ProjectDescription = Column(String(2048), nullable=True)
    ProjectStartDate = Column(Date(), nullable=False)
    ProjectEndDate = Column(Date(), nullable=False)
    ProjectProducts = Column(JSON(), nullable=True)

    AddedBy = Column(Integer(), db.ForeignKey("navak_users.id"))
    CreatedTime = Column(DateTime(), default=datetime.datetime.now)
    LastEdit = Column(DateTime(), default=datetime.datetime.now)

    ProductLogs = db.relationship("ProjectExitProductINFO", backref="project", lazy=True)
    EngineersComment = db.relationship("ProjectComments", backref="project", lazy=True)

    def set_public_key(self):
        while True:
            key = str(uuid.uuid4())
            if self.query.filter(self.PublicKey == key).all():
                continue
            else:
                self.PublicKey = key
                break

    def set_project_name(self, name: str) -> bool:
        """
            this method set a name for Project
            and check if its duplicated name return False
            otherWise set the name and return Treu
        """
        if self.query.filter(self.ProjectName == name).first():
            return False
        else:
            self.ProjectName = name
            return True

    def set_last_edit(self):
        self.LastEdit = datetime.datetime.now()


    def get_products_info(self):
        """
            this method return project's product
            in form of
            [
                {'productname', 'productpartnumber', 'productQuantityRequested'}
            ]
        """
        if self.ProjectProducts == "{}":
            return "NULL"

        try:
            products = json.loads(self.ProjectProducts)
        except json.JSONDecodeError:
            return False

        data = []
        for each in products:
            if not (product_db := StoreModel.Product.query.filter(StoreModel.Product.PublicKey == each).first()):
                return False
            temp = {}
            temp["ProductName"] = product_db.ProductName
            temp["ProductPartNumber"] = product_db.ProductPartNumber
            temp["ProductQT"] = products[each]
            temp["ProductKey"] = each
            data.append(temp)

        return data

    def get_product_qty(self, product_key):
        """
            this method take a product PublicKey and
            check in project products
            and return number of that product is completed in store and handed to staff
        """
        try:
            data = json.loads(self.ProjectProducts)
        except json.JSONDecodeError:
            return False

        if product_key in data:

            return data[product_key].split("/")[0]
        else:
            return False

    def get_products(self):
        """
            this method return all products that belongs to this project
        """
        return json.loads(self.ProjectProducts)



class VacationRequestHandler(db.Model):
    """
        base Model For users that handler Vacation request
    """
    __tablename__ = "navak_vacation_request_handler"

    id = Column(Integer(), primary_key=True)
    UserId = Column(Integer(), db.ForeignKey("navak_users.id"))
    WorkPositionId = Column(Integer(), db.ForeignKey("navak_work_position.id"))



