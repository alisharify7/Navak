from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


SessionServer = Session()
db = SQLAlchemy()
db_migrate = Migrate()
csrf = CSRFProtect()