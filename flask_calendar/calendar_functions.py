from flask_calendar.app import app, db
from flask_calendar.db_setup import init_db, db_session
from flask import flash, current_app, session, render_template, request, redirect, jsonify, abort
from flask_calendar.models import Project, Api, Apikeys, Pms
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from datetime import datetime
import calendar
import json
import hashlib

def check_calendar_duty(duty,y,m,d):
    current_day, current_month, current_year = GregorianCalendar.current_date()
    if y:
        year = int(y)
    else:
        year = int(current_year)
    if m:
        month = int(m)
    else:
        month = int(current_month)
    
    if d:
        current_day= d
    calendar_id = current_app.config["DEFAULT_CALENDAR"]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    data = calendar_data.load_calendar(calendar_id)
    tasks = calendar_data.tasks_from_calendar(year, month, data)
    rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
    jsondata=json.loads(json.dumps(tasks))
    found=''

    filterlist=month
    try:
        found=list(filter(lambda x:x["duty1"]==duty,jsondata[str(filterlist)][str(current_day)]))


    except Exception as err:
        False
    if found == [] or not found:

        jsondata=json.loads(json.dumps(rtasks))
        try:
            found=list(filter(lambda x:x["duty1"]==duty,jsondata[str(filterlist)][str(current_day)]))

        except Exception:
            return ' '
            
    if found:
        return "X"
    else:
        return " "

def get_duty_project(duty):
    prj = db_session.query(Project.project).filter(Project.name==duty).all()
    prj = [item[0] for item in prj]
    prj=prj[0]
    return prj

def get_day_of_week(y,m,d):
    day=(datetime(int(y),int(m),int(d)).strftime('%a'))
    return day

def get_dutys():
    dutys = db_session.query(Project.name).all()
    dutys = [item[0] for item in dutys]
    return dutys

def getphone(duty):
    phones = db_session.query(Project.phone).filter(Project.name==duty).all()
    phones = [item[0] for item in phones]
    phone=phones[0]
    return phone

def auth_api(username,token):
    try:
        tokenkey = (db_session.query(Apikeys.key).filter(Apikeys.user==username).first())[0]
        hash_algoritm = hashlib.new("sha256")
        password_salt=current_app.config["PASSWORD_SALT"]
        hash_algoritm.update((token + password_salt).encode("UTF-8"))
        encoded = hash_algoritm.hexdigest()
        print(encoded)
        print(tokenkey)
    except Exception:
        return False
    if encoded == tokenkey:
        return True
    else:
        return False 