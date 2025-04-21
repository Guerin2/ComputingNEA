from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

def get_uuid():
    return uuid4().hex



