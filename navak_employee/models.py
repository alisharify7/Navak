import uuid

import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, Float, DateTime, BigInteger
from werkzeug.security import check_password_hash, generate_password_hash

from navak.extensions import db

class Education(db.Model):
    """
        base Model For keep all degree of education
    """
    __tablename__ = "navak_education_degree"
    id = Column(Integer(), primary_key=True)
    Name = Column(String(64), nullable=False, unique=True)
    employee = db.relationship("Employee", backref="education", lazy=True)


class WorkPosition(db.Model):
    """
        base Model For keep all WorkPositions
    """
    __tablename__ = "navak_work_position"
    id = Column(Integer(), primary_key=True)
    Name = Column(String(64), nullable=False, unique=True)
    employee = db.relationship("Employee", backref="workposition", lazy=True)



class WorkReport(db.Model):
    """
        base Model For keep all WorkPositions
    """
    __tablename__ = "navak_work_report"
    id = Column(Integer(), primary_key=True)
    EmployeeId = Column(Integer(), db.ForeignKey("navak_employee.id"))
    ReportBody = Column(String(1024), nullable=False)
    ReportDate = Column(Date(), default=datetime.date.today)
    CreatedTime = Column(DateTime(), default=datetime.datetime.now)



class Employee(db.Model):
    """
        Base Model For all Employee's
    """
    __tablename__ = "navak_employee"

    id = Column(Integer(), primary_key=True)

    UserName = Column(String(64), nullable=False, unique=True)
    password = Column(String(102), nullable=False)
    FirstName = Column(String(64), nullable=False)
    LastName = Column(String(64), nullable=False)
    FatherName = Column(String(64), nullable=False)
    BirthDay = Column(Date(), nullable=True)
    MeliCode = Column(String(32), nullable=True, unique=True)
    BirthLocation = Column(String(64), nullable=True)
    PhoneNumber = Column(String(11), nullable=True, unique=True)
    EmergencyPhone = Column(String(11), nullable=True)
    Address = Column(String(256), nullable=True)

    Education = Column(Integer(), db.ForeignKey("navak_education_degree.id"), nullable=True)
    StaffCode = Column(Integer(), nullable=False, unique=True)

    ContractType = Column(String(64), nullable=True)
    StartContract = Column(Date(), nullable=False)
    EndContract = Column(Date(), nullable=False)

    WorkPosition = Column(Integer(), db.ForeignKey("navak_work_position.id"), nullable=False)
    VacationHourTotal = Column(Float(), nullable=False)
    VacationHourTaken = Column(Float(), nullable=False)
    PublicKey = Column(String(36), unique=True, nullable=False)

    Married = Column(Boolean(), nullable=False)
    Children = Column(Integer(), nullable=True, default=0)
    BaseSalary = Column(BigInteger(), nullable=False)

    Created_Time = Column(DateTime(), nullable=False, default=datetime.datetime.now)

    Active = Column(Boolean(), default=False)
    EmployeeTrffic = db.relationship("TrafficControl", backref="employee", lazy=True)
    WorkReports = db.relationship("WorkReport", backref="employee", lazy=True)

    def set_public_key(self):
        """
            this Method Set Unique PublicKey For each Employee Object
        """
        while True:
            key = str(uuid.uuid4())
            key_db = Employee.query.filter(Employee.PublicKey == key).first()
            if not key_db:
                self.PublicKey = key
                return True
            else:
                continue

    def __str__(self):
        return f"{self.id}-{self.FirstName} {self.LastName}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def calculate_vacation_hour(self):
        """
            this Method calculate vacation hour for each employee by its contract time
            each 30 days => 2.5 Day vacation
        """
        day_delta = (self.EndContract - self.StartContract).days
        vacation = ((day_delta / 30) * 2.5) * 8

        # format number to 1 digit after point ==> 2.59898989: 2.6
        vacation = round(vacation)
        self.VacationHourTotal = vacation
        self.VacationHourTaken = 0


    def get_total_vacation(self):
        """
            this method return employee total vacation in hour
        """
        return self.VacationHourTotal

    def set_vacation_total_value(self, value):
        """
            this method update user vacation total value
        """
        self.VacationHourTotal -= value
        self.VacationHourTaken += value


    def set_username(self, username: str):
        """
            this method set username for employee
            and check if username used by another user
            return False

            :params: username:str
            :return: True is username set currectlly Otherwise False
        """
        if (Employee.query.filter(Employee.UserName == username).first()):
            return False
        else:
            self.UserName = username
            return True

    def set_phone_number(self, phonenumber: str):
        """
            this method set phoneumber for employee
            and check if phonenumber used by another user
            return False

            :params: phonenumber:str
            :return: True is phone number set currectlly Otherwise False
        """
        if (Employee.query.filter(Employee.PhoneNumber == phonenumber).first()):
            return False
        else:
            self.PhoneNumber = phonenumber
            return True

    def set_staff_code(self, staffcode: str):
        """
            this method set staff code for employee
            and check if staff code used by another user
            return False

            :params: staff code:str
            :return: True is staff code set currectlly Otherwise False
        """
        if (Employee.query.filter(Employee.StaffCode == staffcode).first()):
            return False
        else:
            self.StaffCode = staffcode
            return True

    def set_meli_code(self, melicode: str):
        """
            this method set meli code for employee
            and check if meli code used by another user
            return False

            :params: meli code:str
            :return: True is meli code set currectlly Otherwise False
        """
        if (Employee.query.filter(Employee.MeliCode == melicode).first()):
            return False
        else:
            self.MeliCode = melicode
            return True


class VacationRequest(db.Model):
    """
        base model for keep all vacation request
        for all employees
    """
    __tablename__ = "navak_vacation_request"

    id = Column(Integer(), primary_key=True)
    Employee_id = Column(Integer(), db.ForeignKey("navak_employee.id"))

    RequestTitle = Column(String(64), nullable=True)
    RequestCaption = Column(String(256), nullable=True)

    # in hour
    RequestedValue = Column(Integer(), nullable=True)
    RequestedDate = Column(Date())

    RequestDate = Column(Date(), default=datetime.date.today)
    RequestDateTime = Column(DateTime(), default=datetime.datetime.now)

    VacationStatus = Column(String(32), default="در انتظار تایید")

    # keep this field here for query
    WorkPositionId = Column(Integer(), db.ForeignKey("navak_work_position.id"))

    ApprovedBy = Column(Integer(), db.ForeignKey("navak_users.id"))

    PublicKey = Column(String(36), nullable=False, unique=True)
    def set_public_key(self):
        key = str(uuid.uuid4())
        while True:
            if self.query.filter(self.PublicKey == key).first():
                continue
            else:
                self.PublicKey = key
                break
