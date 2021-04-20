from flask_calendar.app import db



class Project(db.Model):
    """"""
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    project = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)

class Api(db.Model):
    """"""
    __tablename__ = "api"
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String)
    api = db.Column(db.String)

class Apikeys(db.Model):
    """"""
    __tablename__ = "apikeys"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    key = db.Column(db.String)
    date = db.Column(db.DateTime(timezone=True), default=db.func.now())

class Pms(db.Model):
    """"""
    __tablename__ = "pms"
    id = db.Column(db.Integer, primary_key=True)
    manager = db.Column(db.String)
    project = db.Column(db.String)
    email = db.Column(db.String)