from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func


engine = create_engine('sqlite:///duty.db', echo=True)
Base = declarative_base()

class Project(Base):
    """"""
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    project = Column(String)
    phone = Column(String)
    email = Column(String)

class Api(Base):
    """"""
    __tablename__ = "api"
    id = Column(Integer, primary_key=True)
    project = Column(String)
    api = Column(String)

class Apikeys(Base):
    """"""
    __tablename__ = "apikeys"
    id = Column(Integer, primary_key=True)
    user = Column(String)
    key = Column(String)
    date = Column(DateTime(timezone=True), default=func.now())
# create tables
Base.metadata.create_all(engine)