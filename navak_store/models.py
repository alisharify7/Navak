import uuid

import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, ForeignKey, Date, BigInteger

from navak.extensions import db


class Product(db.Model):
    __tablename__ = "navak_products"

    id = Column(Integer(), primary_key=True)
    PublicKey = Column(String(36), unique=True, nullable=False)

    ProductName = Column(String(256), nullable=False, unique=True)
    ProductPartNumber = Column(String(256), unique=True, nullable=False)
    ProductStoreId = Column(String(256), unique=True, nullable=False)

    ProductDescription = Column(String(2048), nullable=False)
    ProductType = Column(String(128), nullable=False)
    ProductManufacture = Column(String(256), nullable=False)
    ProductPrice = Column(Float(), nullable=False)
    ProductBuyFrom = Column(String(128), nullable=False)
    ProductQuantity = Column(BigInteger(), nullable=False)
    ProductEnterDate = Column(Date(), nullable=False)
    ProductPackage = Column(String(128), nullable=False)
    ProductBringPerson = Column(String(128), nullable=False)
    ProductStatus = Column(Boolean(), nullable=True)
    CreatedTime = Column(DateTime(), default=datetime.datetime.now, nullable=False)
    LastEdit = Column(DateTime(), default=datetime.datetime.now, nullable=False, onupdate=datetime.datetime.now)
    AddedBy = Column(Integer(), ForeignKey("navak_users.id"), nullable=False)

    # later set new table for this record
    # ProductBringOutPerson = Column(String(128), nullable=False)

    def set_public_key(self):
        while True:
            key = str(uuid.uuid4())
            if Product.query.filter(Product.PublicKey == key).first():
                continue
            else:
                self.PublicKey = key
                break

    def set_update_time(self):
        self.LastEdit = khayyam.JalaliDatetime.now()


    def update_product_name(self, productname:str):
        """
            this method take a new product name and check if its not duplicated
            replace it for this object
        """
        if not(Product.query.filter(Product.ProductName == productname).first()):
            self.ProductName = productname
            return True
        else:
            return False


    def update_product_part_number(self, partnumber:str):
        """
            this method take a new product name and check if its not duplicated
            replace it for this object
        """
        if not(Product.query.filter(Product.ProductPartNumber == partnumber).first()):
            self.ProductPartNumber = partnumber
            return True
        else:
            return False

    def update_product_store_id(self, storeid: str):
        """
            this method take a new product name and check if its not duplicated
            replace it for this object
        """
        if not (Product.query.filter(Product.ProductStoreId == storeid).first()):
            self.ProductStoreId = storeid
            return True
        else:
            return False


class PersonExitProduct(db.Model):
    """
        this table use for logging exit product that exited by a person
        : not for a project :
    """
    __tablename__ = "navak_person_exit_product"
    id = Column(Integer(), primary_key=True)
    ExitedProductId = Column(Integer(), nullable=False)
    ExitedProductQTY = Column(Integer(), nullable=False)

    PersonExitProductInfo = Column(Integer(), db.ForeignKey("navak_person_exit_product_info.id"))


class PersonExitProductINFO(db.Model):
    """
        this table use for logging exit product that exited by a person
        : not for a project :
    """
    __tablename__ = "navak_person_exit_product_info"
    id = Column(Integer(), primary_key=True)

    SysLogExit = Column(String(2048), nullable=False, unique=False)
    Description = Column(String(2048), nullable=False, unique=False)
    ExitedDateTime = Column(DateTime(), default=datetime.datetime.now, nullable=False)
    PersonName = Column(String(128), nullable=False, unique=False)

    ExitProductLog = db.relationship("PersonExitProduct", backref="PersonExitProductINFOobj", lazy=True)




class ProjectExitProduct(db.Model):
    """
        this table use for logging exit product that belong a project
    """
    __tablename__ = "navak_project_exit_product"
    id = Column(Integer(), primary_key=True)
    ProjectExitProductINFOtId = Column(Integer(), db.ForeignKey("navak_project_exit_product_info.id"))
    ExitedProductId = Column(Integer(), nullable=False)
    ExitedProductQTY = Column(Integer(), nullable=False)

class ProjectExitProductINFO(db.Model):
    """
        this table use for logging exit product that belong a project
    """
    __tablename__ = "navak_project_exit_product_info"
    id = Column(Integer(), primary_key=True)
    PersonName = Column(String(128), nullable=False, unique=False)
    ProjectId = Column(Integer(), db.ForeignKey("navak_project.id"), nullable=False, unique=False)
    Description = Column(String(2048), nullable=False, unique=False)
    SysLogExit = Column(String(2048), nullable=False, unique=False)
    ExitedDateTime = Column(DateTime(), default=datetime.datetime.now, nullable=False)


    ExitProductLog = db.relationship("ProjectExitProduct", backref="ProjectExitProductOBJ", lazy=True)



