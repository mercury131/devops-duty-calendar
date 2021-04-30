from flask import Flask, flash, current_app, session, render_template, request, redirect, jsonify, abort
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.models import Project, Pms, Apikeys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from flask_calendar.app import app
from flask_calendar.call_providers import send_email
from datetime import datetime, timedelta
from sqlalchemy import and_



def get_project_manager(project):
    try:    
        manager = db_session.query(Pms.email).filter(Pms.project==project).all()
        manager = [item[0] for item in manager]
        manager=manager[0]
        return manager
    except Exception:
        return None

def getemail(duty):
    try:
        emails = db_session.query(Project.email).filter(Project.name==duty).all()
        emails = [item[0] for item in emails]
        email=emails[0]
        return email
    except Exception:
        return None

def get_project_managers():
    managers = db_session.query(Pms.project).all()
    managers = [item[0] for item in managers]
    managers =list(set(managers))
    return managers

def get_projects():
    projects = db_session.query(Project.project).all()
    projects = [item[0] for item in projects]
    projects =list(set(projects))
    return projects

def check_today_duty(project,app):
    with app.app_context():
        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = int(current_year)
        month = int(current_month)
        calendar_id = current_app.config["DEFAULT_CALENDAR"]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
        data = calendar_data.load_calendar(calendar_id)
        tasks = calendar_data.tasks_from_calendar(year, month, data)
        rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
        jsondata=json.loads(json.dumps(tasks))
        found=''
        filterlist=str(current_month)
        try:
            found=list(filter(lambda x:x["project"]==project,jsondata[filterlist][str(current_day)]))
        except Exception:
            jsondata=json.loads(json.dumps(rtasks))
            try:
                found=list(filter(lambda x:x["project"]==project,jsondata[str(current_month)][str(current_day)]))
                return True
            except Exception:
                return False
                
        if found:
            return True
        else:
            return False
        
def get_today_duty(project,app):
    with app.app_context():
        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = int(current_year)
        month = int(current_month)
        calendar_id = current_app.config["DEFAULT_CALENDAR"]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
        data = calendar_data.load_calendar(calendar_id)
        tasks = calendar_data.tasks_from_calendar(year, month, data)
        rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
        jsondata=json.loads(json.dumps(tasks))
        found=''
        filterlist=str(current_month)
        try:
            found=list(filter(lambda x:x["project"]==project,jsondata[filterlist][str(current_day)]))
        except Exception:
            jsondata=json.loads(json.dumps(rtasks))

            try:
                found=list(filter(lambda x:x["project"]==project,jsondata[str(current_month)][str(current_day)]))
            except Exception:
                return jsonify("No duty found for ",project," today","Check your project schedule!")
        if found:
            True
        else:
            return jsonify("No duty found for ",project," today","Check your project schedule!")
        if len(found) > 1:
            for x in found:
                duty1=x['duty1']
        else:
            duty1=found[0]['duty1']
        
        return duty1

def get_yesterday_duty(project,app):
    with app.app_context():
        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = int(current_year)
        month = int(current_month)
        yesterday = datetime.now() - timedelta(1)
        yesterday = datetime.strftime(yesterday, '%d')
        calendar_id = current_app.config["DEFAULT_CALENDAR"]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
        data = calendar_data.load_calendar(calendar_id)
        tasks = calendar_data.tasks_from_calendar(year, month, data)
        rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
        jsondata=json.loads(json.dumps(tasks))
        found=''
        filterlist=str(current_month)
        try:
            found=list(filter(lambda x:x["project"]==project,jsondata[filterlist][str(yesterday)]))
        except Exception:
            jsondata=json.loads(json.dumps(rtasks))
            try:
                found=list(filter(lambda x:x["project"]==project,jsondata[str(current_month)][str(yesterday)]))
            except Exception:
                return None
        if found:
            True
        else:
            False
        if len(found) > 1:
            for x in found:
                duty1=x['duty1']
        else:
            duty1=found[0]['duty1']
        
        return duty1

def checkpm():
    with app.app_context():
        projects=get_projects()
        for project in projects:
            email=get_project_manager(project)
            duty=check_today_duty(project,app)
            if duty is False:
                if email:
                    subject = (current_app.config["SH_PM_EMAIL_SUBJECT"] )
                    text = current_app.config["SH_PM_EMAIL_MESSAGE"]
                    receiver_address = email
                    smtp_server = current_app.config["SH_SMTP_SERVER"]
                    smtp_port = current_app.config["SH_SMTP_PORT"]
                    sender_address = current_app.config["SH_SENDER_ADDRESS"]
                    smtp_server_login = current_app.config["SH_SMTP_LOGIN"]
                    smtp_server_password = current_app.config["SH_SMTP_PASSWORD"]
                    if smtp_server_login == '':
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    else:
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    print("Send notification to ",email)


def check_duty_schedule():
    with app.app_context():
        projects=get_projects()

        for project in projects:
            duty=None
            last_duty=None
            email=None
            lemail=None
            duty=get_today_duty(project,app)
            last_duty=get_yesterday_duty(project,app)
            if last_duty != duty:
                email=getemail(duty)
                if email:
                    subject = (current_app.config["SH_DUTY_EMAIL_SUBJECT"] ).replace('<PROJECT>',project)
                    text = current_app.config["SH_DUTY_EMAIL_MESSAGE"].replace('<PROJECT>',project)
                    receiver_address = email
                    smtp_server = current_app.config["SH_SMTP_SERVER"]
                    smtp_port = current_app.config["SH_SMTP_PORT"]
                    sender_address = current_app.config["SH_SENDER_ADDRESS"]
                    smtp_server_login = current_app.config["SH_SMTP_LOGIN"]
                    smtp_server_password = current_app.config["SH_SMTP_PASSWORD"]
                    if smtp_server_login == '':
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    else:
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    print("Send notification to ",email)


                lemail=getemail(last_duty)
                if email:
                    subject = (current_app.config["SH_LAST_DUTY_EMAIL_SUBJECT"] ).replace('<PROJECT>',project)
                    text = current_app.config["SH_LAST_DUTY_EMAIL_MESSAGE"].replace('<PROJECT>',project)
                    receiver_address = lemail
                    smtp_server = current_app.config["SH_SMTP_SERVER"]
                    smtp_port = current_app.config["SH_SMTP_PORT"]
                    sender_address = current_app.config["SH_SENDER_ADDRESS"]
                    smtp_server_login = current_app.config["SH_SMTP_LOGIN"]
                    smtp_server_password = current_app.config["SH_SMTP_PASSWORD"]
                    if smtp_server_login == '':
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    else:
                        try:
                            send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                        except Exception:
                            print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                    print("Send notification to ",email)                    


def check_token_ttl():
    with app.app_context():    
        current_time = datetime.utcnow()
        year_ago = current_time - timedelta(days=365)
        notify_time = current_time - timedelta(days=335)
        token_to_notify = db_session.query(Apikeys.user).filter(Apikeys.date <= notify_time).all()
        token_to_delete = db_session.query(Apikeys.user).filter(Apikeys.date <= year_ago).all()
        if token_to_notify:
            token_to_notify = [item[0] for item in token_to_notify]
            for user in token_to_notify:
                print("Token for user",user,"will expire soon. Please update your token!")
                subject = ("Token for user " + user +" will be expire soon. Please update your token!")
                text = ("Token for user " + user + " will be expire soon. Please update your token!")
                receiver_address = current_app.config["SH_ADMINISTRATOR_EMAIL"]
                email = receiver_address
                smtp_server = current_app.config["SH_SMTP_SERVER"]
                smtp_port = current_app.config["SH_SMTP_PORT"]
                sender_address = current_app.config["SH_SENDER_ADDRESS"]
                smtp_server_login = current_app.config["SH_SMTP_LOGIN"]
                smtp_server_password = current_app.config["SH_SMTP_PASSWORD"]
                if smtp_server_login == '':
                    try:
                        send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address)
                    except Exception:
                        print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                else:
                    try:
                        send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                    except Exception:
                        print("Error while sending email message to:",email,"detected","Check SMTP server settings")
                print("Send notification to ",email)              
        if token_to_delete:
            token_to_delete = [item[0] for item in token_to_delete]
            for user in token_to_delete:
                print("Delete Token for user",user)
            db_session.query(Apikeys.user).filter(Apikeys.date <= year_ago).delete(synchronize_session=False)
            db_session.commit()
            



def start_scheduler(app):
    with app.app_context():
        jobs=app.config['JOBS']
        for job in jobs:
            jobday=None
            jobhour=None
            try:
                jobday=(job['day'])
                jobhour=(job['hour'])
            except:
                print("not cron job")
            if jobday and jobhour:
                print("add job",job['id'])
                app.scheduler.add_job(eval(job['func']), trigger=job['trigger'], day=job['day'], hour=job['hour'], minute=job['minute'])
            elif (job['trigger']) == 'interval':
                print("add job",job['id'])
                app.scheduler.add_job(eval(job['func']), trigger=job['trigger'], seconds=job['seconds'])