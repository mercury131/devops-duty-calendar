from flask import Flask, flash, current_app, session, render_template, request, redirect, jsonify, abort, send_file
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.models import Project, Pms, Apikeys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from flask_calendar.app import app
from flask_calendar.call_providers import send_email, send_rest1
from datetime import datetime, timedelta
from sqlalchemy import and_
import calendar

import pandas as pd
from io import BytesIO
import xlsxwriter

from flask_calendar.calendar_functions import check_calendar_duty, get_duty_project, get_day_of_week, get_dutys

def export_to_excel(m,y):
    with app.app_context():
        if m:
            month_days= int(calendar.monthrange(int(y), int(m))[1])
            month_name = GregorianCalendar.MONTH_NAMES[int(m) - 1]
        else:
            now = datetime.now()
            month_days= int(calendar.monthrange(now.year, now.month)[1])
            month_name = mydate = now.strftime("%B")
            m=now.strftime("%m")

        if y:
            year=int(y)
        else:
            y=int(datetime.now().year)

        if request.method == 'POST':
            date = request.form.get("date", "")
            fragments = re.split("-", date)
            try:
                m = int(fragments[1])
                month = max(min(m, 12), 1)
                month_name = GregorianCalendar.MONTH_NAMES[month - 1]
                y = int(fragments[0])
                month_days= int(calendar.monthrange(y, m)[1])
            except Exception:
                False

        month_days=list(range(1,(month_days + 1)))
        dutys=get_dutys()
        days=month_days
        data={}

        for duty in dutys:
            tmp_list=[]
            duty_days=0
            for day in days:
                if check_calendar_duty(duty,y,m,day) == 'X':
                    duty_days=duty_days + 1
                tmp_list.append(check_calendar_duty(duty,y,m,day))
            tmp_list.insert(len(tmp_list),duty_days)
            tmp_list.insert(0,str(get_duty_project(duty)))
            data[str(duty)] = tmp_list

        days_week=['Project']
        for day in days:
            days_week.append( str(day) + ' ' +  str(get_day_of_week(y,m,day)) )
        days_week.insert(len(days_week),"Days")
        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = days_week
        df.index.name = 'Name'
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=('Duty Report' + ' ' + str(m) + '-' + str(y)))
        writer.save()
        output.seek(0)
        excel_file=output
        return send_file(excel_file, attachment_filename='report.xlsx', as_attachment=True)
