from flask import Flask, flash, current_app, session, render_template, request, redirect, jsonify, abort, send_file
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.models import Project, Pms, Apikeys
from flask_calendar.calendar_functions import getphone, auth_api
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from flask_calendar.app import app
from flask_calendar.call_providers import send_email, send_rest1
from datetime import datetime, timedelta
from sqlalchemy import and_
import calendar

from flask_calendar.calendar_functions import check_calendar_duty, get_duty_project, get_day_of_week, get_dutys

def get_current_duty_api(prj,username,token):
        
        err = 0
        auth_result=auth_api(username,token)
        print(auth_result)

        if auth_result is not True:
            abort(404)

        project=prj
        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = int(request.args.get("y", current_year))
        year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
        month = int(request.args.get("m", current_month))
        month = max(min(month, 12), 1)
        calendar_id = current_app.config["DEFAULT_CALENDAR"]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
        data = calendar_data.load_calendar(calendar_id)
        tasks = calendar_data.tasks_from_calendar(year, month, data)
        rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
        jsondata=json.loads(json.dumps(tasks))
        filterlist=str(current_month)
        try:
            found=list(filter(lambda x:x["project"]==project,jsondata[filterlist][str(current_day)]))
        except Exception:
            jsondata=json.loads(json.dumps(rtasks))
            try:
                found=list(filter(lambda x:x["project"]==project,jsondata[str(current_month)][str(current_day)]))
            except Exception:
                return jsonify("No duty found for ",project," today","Check your project schedule!"), 500
        if found:
            print(found)
        else:
            return jsonify("No duty found for ",project," today","Check your project schedule!"), 500
        if len(found) > 1:
            for x in found:
                duty1=x['duty1']
                duty2=x['duty2']
        else:
            duty1=found[0]['duty1']
            duty2=found[0]['duty2']

        phone1=getphone(duty1)
        phone2=getphone(duty2)
        duty_information = {'Project': project, 'Current_duty': duty1, 'Active_phone': phone1, 'Secondary_duty': duty2, 'Secondary_phone': phone2 }
        return jsonify(duty_information), 200
