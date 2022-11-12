from flask_calendar.app import app, db
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.forms import SearchForm, Duty, ApiForm, PMForm
from flask import flash, current_app, session, render_template, request, redirect, jsonify, abort, send_file
from flask_calendar.models import Project, Api, Apikeys, Pms
from flask_calendar.tables import Results, Apitable, PMtable
from flask_calendar.app_utils import remove_session , get_session_username
from flask_calendar.constants import SESSION_ID
from flask_calendar.authentication import Authentication
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.call_providers import send_to_telegram, send_to_slack, send_email, send_rest1
from flask_calendar.call_api import get_current_duty_api
from datetime import datetime
import calendar
import json
import hashlib
from uuid import uuid4
import re
import os
from flask_calendar.scheduler import start_scheduler
from flask_calendar.export_to_excel import export_to_excel

from flask_calendar.app_utils import (
    add_session,
    authenticated,
    authorized,
    get_session_username,
    new_session_id,
    next_month_link,
    previous_month_link,
)
init_db()
app=app

def getphone(duty):
    phones = db_session.query(Project.phone).filter(Project.name==duty).all()
    phones = [item[0] for item in phones]
    phone=phones[0]
    return phone

def getemail(duty):
    emails = db_session.query(Project.email).filter(Project.name==duty).all()
    emails = [item[0] for item in emails]
    email=emails[0]
    return email


def get_duty_project(duty):
    prj = db_session.query(Project.project).filter(Project.name==duty).all()
    prj = [item[0] for item in prj]
    prj=prj[0]
    return prj

def get_dutys():
    dutys = db_session.query(Project.name).all()
    dutys = [item[0] for item in dutys]
    return dutys

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

def get_day_of_week(y,m,d):
    day=(datetime(int(y),int(m),int(d)).strftime('%a'))
    return day

def get_project_api(prj):
    apis = db_session.query(Api.api).filter(Api.project==prj).all()
    apis = [item[0] for item in apis]
    try:
        apis = apis[0].split(',')
        return apis
    except Exception:
        return ''
    

@app.route('/allduty')
@authenticated
def show_dutys():
    results = []
    qry = db_session.query(Project)
    results = qry.all()
    # display results
    tableres = Results(results)
    tableres.border = True
    if session['admin'] == 'true' :
        return render_template('duty.html', table=tableres)
    else:
        return redirect("/", code=302)

@app.route('/pms')
@authenticated
def show_pms():
    results = []
    qry = db_session.query(Pms)
    results = qry.all()
    # display results
    tableres = PMtable(results)
    tableres.border = True
    if session['admin'] == 'true' :
        return render_template('pms.html', table=tableres)
    else:
        return redirect("/", code=302)

@app.route('/add_pm', methods=['GET', 'POST'])
@authenticated
def add_pm():
    """
    Add a new pm
    """
    form = PMForm(request.form)
    if session['admin'] == 'true' :
        if request.method == 'POST' and form.validate():
            # save the pm
            pm = Pms()
            save_pm(pm, form, new=True)
            flash('pm add created successfully!')
            return redirect('/')
        return render_template('add_pm.html', form=form)
    else:
        return redirect("/", code=302)


@app.route('/pmitem/<int:id>', methods=['GET', 'POST'])
@authenticated
def edit_pm(id):
    if session['admin'] == 'true' :
        qry = db_session.query(Pms).filter(
                    Pms.id==id)
        pm = qry.first()
        if pm:
            form = PMForm(formdata=request.form, obj=pm)
            if request.method == 'POST' and form.validate():
                # save edits
                save_pm(pm, form)
                flash('PM updated successfully!')
                return redirect('/')
            return render_template('edit_pm.html', form=form)
        else:
            return 'Error loading #{id}'.format(id=id)
    else:
        return redirect("/", code=302)


@authenticated
def save_pm(pm, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    if new:
        pm = Pms()
        pm.manager = form.manager.data
        pm.project = form.project.data
        pm.email = form.email.data
        db_session.add(pm)
    else:
        pm.manager = form.manager.data
        pm.project = form.project.data
        pm.email = form.email.data
    # commit the data to the database
    db_session.commit()


@app.route('/deletepm/<int:id>', methods=['GET', 'POST'])
@authenticated
def delete_pm(id):
    if session['admin'] == 'true' :
            
        """
        Delete the item in the database that matches the specified
        id in the URL
        """
        qry = db_session.query(Pms).filter(
            Pms.id==id)
        pm = qry.first()
        if pm:
            form = PMForm(formdata=request.form, obj=pm)
            if request.method == 'POST' and form.validate():
                # delete the item from the database
                db_session.delete(pm)
                db_session.commit()
                flash('PM deleted successfully!')
                return redirect('/')
            return render_template('delete_pm.html', form=form)
        else:
            return 'Error deleting #{id}'.format(id=id)
    else:
        return redirect("/", code=302)

@app.route('/apisettings')
@authenticated
def show_apisettings():
    results = []
    qry = db_session.query(Api)
    results = qry.all()
    # display results
    tableres = Apitable(results)
    tableres.border = True
    if session['admin'] == 'true' :
        return render_template('api.html', table=tableres)
    else:
        return redirect("/", code=302)

@app.route('/add_api', methods=['GET', 'POST'])
@authenticated
def add_api():
    """
    Add a new api mapping
    """
    form = ApiForm(request.form)
    if session['admin'] == 'true' :
        if request.method == 'POST' and form.validate():
            # save the duty
            api = Api()
            save_api_mapping(api, form, new=True)
            flash('api mapping created successfully!')
            return redirect('/')
        return render_template('add_api.html', form=form)
    else:
        return redirect("/", code=302)

@authenticated
def save_api_mapping(api, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    if new:
        api = Api()
        api.project = form.project.data
        api.api = form.api.data
        db_session.add(api)
    else:
        #duty = Project()
        api.project = form.project.data
        api.api = form.api.data
    # commit the data to the database
    db_session.commit()

@app.route('/apiitem/<int:id>', methods=['GET', 'POST'])
@authenticated
def edit_api_mapping(id):
    if session['admin'] == 'true' :
        qry = db_session.query(Api).filter(
                    Api.id==id)
        api = qry.first()
        if api:
            form = ApiForm(formdata=request.form, obj=api)
            if request.method == 'POST' and form.validate():
                # save edits
                save_api_mapping(api, form)
                flash('Api mapping updated successfully!')
                return redirect('/')
            return render_template('edit_api.html', form=form)
        else:
            return 'Error loading #{id}'.format(id=id)
    else:
        return redirect("/", code=302)

@app.route('/deleteapi/<int:id>', methods=['GET', 'POST'])
@authenticated
def delete_api_mapping(id):
    if session['admin'] == 'true' :
            
        """
        Delete the item in the database that matches the specified
        id in the URL
        """
        qry = db_session.query(Api).filter(
            Api.id==id)
        api = qry.first()
        if api:
            form = ApiForm(formdata=request.form, obj=api)
            if request.method == 'POST' and form.validate():
                # delete the item from the database
                db_session.delete(api)
                db_session.commit()
                flash('Api mapping deleted successfully!')
                return redirect('/')
            return render_template('delete_api.html', form=form)
        else:
            return 'Error deleting #{id}'.format(id=id)
    else:
        return redirect("/", code=302)

@app.route('/new_duty', methods=['GET', 'POST'])
@authenticated
def new_duty():
    """
    Add a new duty
    """
    form = Duty(request.form)
    if session['admin'] == 'true' :
        if request.method == 'POST' and form.validate():
            # save the duty
            duty = Duty()
            save_changes(duty, form, new=True)
            flash('Duty created successfully!')
            return redirect('/')
        return render_template('new_duty.html', form=form)
    else:
        return redirect("/", code=302)

@authenticated
def save_changes(duty, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    if new:
        duty = Project()
        duty.name = form.name.data
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
        db_session.add(duty)
    else:
        #duty = Project()
        oldname = duty.name
        oldphone = duty.phone
        oldemail = duty.email

        duty.name = form.name.data
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
        
        if oldname != duty.name or oldphone != duty.phone or oldemail != duty.email:
            data_folder = app.config["DATA_FOLDER"]
            filename = app.config["DEFAULT_CALENDAR"]
            calendar_file=open(os.path.join(".", data_folder, "{}.json".format(filename)), "rt")
            data = calendar_file.read()
            if oldname != duty.name:
                data = data.replace(oldname, form.name.data)
            if oldphone != duty.phone:
                data = data.replace(oldphone, form.phone.data)
            calendar_file.close()
            calendar_file=open(os.path.join(".", data_folder, "{}.json".format(filename)), "wt")
            calendar_file.write(data)
            calendar_file.close()

    # commit the data to the database
    db_session.commit()

@app.route('/item/<int:id>', methods=['GET', 'POST'])
@authenticated
def edit(id):
    if session['admin'] == 'true' :
        qry = db_session.query(Project).filter(
                    Project.id==id)
        duty = qry.first()
        if duty:
            form = Duty(formdata=request.form, obj=duty)
            if request.method == 'POST' and form.validate():
                # save edits
                save_changes(duty, form)
                flash('Duty updated successfully!')
                return redirect('/')
            return render_template('edit_duty.html', form=form)
        else:
            return 'Error loading #{id}'.format(id=id)
    else:
        return redirect("/", code=302)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@authenticated
def delete(id):
    if session['admin'] == 'true' :
            
        """
        Delete the item in the database that matches the specified
        id in the URL
        """
        qry = db_session.query(Project).filter(
            Project.id==id)
        duty = qry.first()
        if duty:
            form = Duty(formdata=request.form, obj=duty)
            if request.method == 'POST' and form.validate():
                # delete the item from the database
                db_session.delete(duty)
                db_session.commit()
                flash('Duty deleted successfully!')
                return redirect('/')
            return render_template('delete_duty.html', form=form)
        else:
            return 'Error deleting #{id}'.format(id=id)
    else:
        return redirect("/", code=302)

@app.route('/duty_choice/<value>')
@authenticated
def duty_choice(value):
    prj=str("%" + value + "%")
    dutys = db_session.query(Project.name).filter(Project.project.like(prj)).all()
    dutys = [item[0] for item in dutys]
    return jsonify({'DUTY': dutys})

@app.route('/duty_choice2/<value1>&<value2>')
@authenticated
def duty_choice2(value1,value2):
    prj=str("%" + value1 + "%")
    duty=value2
    dutys = db_session.query(Project.name).filter(Project.project.like(prj)).all()
    dutys = [item[0] for item in dutys]
    dutys.append(dutys.pop(dutys.index(duty)))
    return jsonify({'DUTY': dutys})

@app.route('/duty_projects/')
@authenticated
def duty_projects():
    projects = db_session.query(Project.project).all()
    projects = [item[0] for item in projects]
    projects_all=[]
    for item in projects:
        projects_all.append(item.split(','))
    projects =[]
    for item in projects_all:
        for prj in item:
            projects.append((prj))

    projects= list(set(projects))
    projects.insert(0, "Select project")
    return jsonify({'PROJECTS': projects})

@app.route('/api_project/<value>')
@authenticated
def get_api_project(value):
    apiid=value
    prjs = db_session.query(Api.project).filter(Api.id==apiid).all()
    prjs = [item[0] for item in prjs]
    return jsonify({'PROJECT': prjs})




@app.route('/logout/')
@authenticated
def logout():
    session_id = request.cookies.get(SESSION_ID)
    username=get_session_username(session_id)
    remove_session(session_id,username)
    return redirect('/login')

@app.route('/call/<prj>/<username>&<token>', defaults={'secondary': None, 'sendto': None}, methods=['GET', 'POST'])
@app.route('/call/<prj>/<username>&<token>&<secondary>',defaults={'sendto': None}, methods=['GET', 'POST'])
@app.route('/call/<prj>/<username>&<token>&<secondary>&<sendto>', methods=['GET', 'POST'])
def call(prj,username,token,secondary,sendto):
    err = 0
    auth_result=auth_api(username,token)

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

    if secondary:
        phone2=getphone(duty1)
        phone1=getphone(duty2)
    else:
        phone1=getphone(duty1)
        phone2=getphone(duty2)

    apis=get_project_api(project)


    

    if sendto == "telegram" or "telegram" in apis or apis == '' and current_app.config["USE_TELEGRAM"] == 'yes' :
        phone = '+' + phone1
        message=current_app.config["TELEGRAM_MESSAGE"] + " Project: " + project
        api_id=current_app.config["TELEGRAM_API_ID"]
        api_hash=current_app.config["TELEGRAM_API_HASH"]
        token=current_app.config["TELEGRAM_BOT_TOKEN"]
        try:
            send_to_telegram(phone,message,api_id,api_hash,token)
            if len(apis) > 1:
                output=("Send message to:",phone1,"complete successfully")
            else:
                return jsonify("Send message to:",phone1,"complete successfully")
        except Exception:
            if len(apis) > 1:
                err=1
                output=("Error while sending message to:",phone1,"detected","Check Telegram tokens or phone number format")
            else:
                return jsonify("Error while sending message to:",phone1,"detected","Check Telegram tokens or phone number format"), 500
    
    if sendto == "slack" or "slack" in apis or apis == '' and current_app.config["USE_SLACK"] == 'yes' :
        
        if secondary:
            duty = duty2
        else:
            duty = duty1
        message = current_app.config["SLACK_MESSAGE"]
        slackchannel=project
        apitoken=current_app.config["SLACK_APP_TOKEN"]
        try:
            send_to_slack(duty,message,slackchannel,apitoken)
            if len(apis) > 1:
                if 'output' in locals():
                    output=output + ("Send message to:",duty,(" in slack cnannel #" + project + " complete successfully"))
                else:
                    output = ("Send message to:",duty,(" in slack cnannel #" + project + " complete successfully"))
            else:
                return jsonify("Send message to:",duty,(" in slack cnannel #" + project + " complete successfully"))
        except Exception:
            if len(apis) > 1:
                err=1
                if 'output' in locals():
                    output=output + ("Error while sending message to:",duty,"detected","Check Slack tokens or userID format")
                else:
                    output = ("Error while sending message to:",duty,"detected","Check Slack tokens or userID format")
            else:
                return jsonify("Error while sending message to:",duty,"detected","Check Slack tokens or userID format"), 500

    if sendto == "email" or "email" in apis or apis == '' and current_app.config["USE_EMAIL"] == 'yes' :
        if secondary:
            email1=getemail(duty2)
        else:
            email1=getemail(duty1)
        subject = (current_app.config["EMAIL_SUBJECT"] + " Project: " + project)
        text = current_app.config["EMAIL_MESSAGE"]
        receiver_address = email1
        smtp_server = current_app.config["SMTP_SERVER"]
        smtp_port = current_app.config["SMTP_PORT"]
        sender_address = current_app.config["SENDER_ADDRESS"]
        smtp_server_login = current_app.config["SMTP_LOGIN"]
        smtp_server_password = current_app.config["SMTP_PASSWORD"]
        
        if smtp_server_login == '':
            try:
                send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address)
                if len(apis) > 1:
                    if 'output' in locals():
                        output=output + ("Send email message to:",email1," complete successfully")
                    else:
                        output = ("Send email message to:",email1," complete successfully")
                else:
                    return jsonify("Send email message to:",email1," complete successfully")
            except Exception:
                if len(apis) > 1:
                    err=1
                    if 'output' in locals():
                        output=output + ("Error while sending email message to:",email1,"detected","Check SMTP server settings")
                    else:
                        output = ("Error while sending email message to:",email1,"detected","Check SMTP server settings")
                else:
                    return jsonify("Error while sending email message to:",email1,"detected","Check SMTP server settings"), 500
        else:
            #
            try:
                send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                if len(apis) > 1:
                    if 'output' in locals():
                        output=output + ("Send email message to:",email1," complete successfully")
                    else:
                        output = ("Send email message to:",email1," complete successfully")
                else:
                    return jsonify("Send email message to:",email1," complete successfully")
            except Exception:
                if len(apis) > 1:
                    err=1
                    if 'output' in locals():
                        output=output + ("Error while sending email message to:",email1,"detected","Check SMTP server settings")
                    else:
                        output = ("Error while sending email message to:",email1,"detected","Check SMTP server settings")
                else:
                    return jsonify("Error while sending email message to:",email1,"detected","Check SMTP server settings"), 500

    if sendto == "rest1" or "rest1" in apis or apis == '' and current_app.config["USE_REST1"] == 'yes' :
        if secondary:
            email2=getemail(duty1)
            email1=getemail(duty2)
            duty1=phone1
            duty2=phone2
        else:
            email1=getemail(duty1)
            email2=getemail(duty2)
            duty1=phone1
            duty2=phone2
        url=current_app.config["REST1_URL"]
        method=current_app.config["REST1_METHOD"]
        auth=current_app.config["REST1_AUTH"]
        user=current_app.config["REST1_USER"]
        password=current_app.config["REST1_PASSWORD"]
        arg1=current_app.config["REST1_ARG1"]
        arg2=current_app.config["REST1_ARG2"]
        arg3=current_app.config["REST1_ARG3"]
        arg4=current_app.config["REST1_ARG4"]
        try:
            result=send_rest1(duty1,duty2,project,email1,email2,url,method,auth,user,password,arg1,arg2,arg3,arg4)
            if len(apis) > 1:
                if 'output' in locals():
                    output=output + ("Send REST request to:",url," complete successfully")
                else:
                    output = ("Send REST request to:",url," complete successfully")
            else:
                return jsonify("Send REST request to:",url," complete successfully")
        except Exception as ex:
            print(ex)
            if len(apis) > 1:
                err=1
                if 'output' in locals():
                    output=output + ("Error! Cannot send REST request to:",url," check your request!")
                else:
                    output = ("Error! Cannot send REST request to:",url," check your request!")
            else:
                return jsonify("Error! Cannot send REST request to:",url," check your request!")

    if sendto == "rest2" or "rest2" in apis or apis == '' and current_app.config["USE_REST2"] == 'yes' :
        if secondary:
            email2=getemail(duty1)
            email1=getemail(duty2)
            duty1=phone1
            duty2=phone2
        else:
            email1=getemail(duty1)
            email2=getemail(duty2)
            duty1=phone1
            duty2=phone2
        url=current_app.config["REST2_URL"]
        method=current_app.config["REST2_METHOD"]
        auth=current_app.config["REST2_AUTH"]
        user=current_app.config["REST2_USER"]
        password=current_app.config["REST2_PASSWORD"]
        arg1=current_app.config["REST2_ARG1"]
        arg2=current_app.config["REST2_ARG2"]
        arg3=current_app.config["REST2_ARG3"]
        arg4=current_app.config["REST2_ARG4"]
        try:
            result=send_rest1(duty1,duty2,project,email1,email2,url,method,auth,user,password,arg1,arg2,arg3,arg4)
            if len(apis) > 1:
                if 'output' in locals():
                    output=output + ("Send REST request to:",url," complete successfully")
                else:
                    output = ("Send REST request to:",url," complete successfully")
            else:
                return jsonify("Send REST request to:",url," complete successfully")
        except Exception as ex:
            print(ex)
            if len(apis) > 1:
                err=1
                if 'output' in locals():
                    output=output + ("Error! Cannot send REST request to:",url," check your request!")
                else:
                    output = ("Error! Cannot send REST request to:",url," check your request!")
            else:
                return jsonify("Error! Cannot send REST request to:",url," check your request!")

    if sendto == "rest3" or "rest3" in apis or apis == '' and current_app.config["USE_REST3"] == 'yes' :
        if secondary:
            email2=getemail(duty1)
            email1=getemail(duty2)
            duty1=phone1
            duty2=phone2
        else:
            email1=getemail(duty1)
            email2=getemail(duty2)
            duty1=phone1
            duty2=phone2
        url=current_app.config["REST3_URL"]
        method=current_app.config["REST3_METHOD"]
        auth=current_app.config["REST3_AUTH"]
        user=current_app.config["REST3_USER"]
        password=current_app.config["REST3_PASSWORD"]
        arg1=current_app.config["REST3_ARG1"]
        arg2=current_app.config["REST3_ARG2"]
        arg3=current_app.config["REST3_ARG3"]
        arg4=current_app.config["REST3_ARG4"]
        try:
            result=send_rest1(duty1,duty2,project,email1,email2,url,method,auth,user,password,arg1,arg2,arg3,arg4)
            if len(apis) > 1:
                if 'output' in locals():
                    output=output + ("Send REST request to:",url," complete successfully")
                else:
                    output = ("Send REST request to:",url," complete successfully")
            else:
                return jsonify("Send REST request to:",url," complete successfully")
        except Exception as ex:
            print(ex)
            if len(apis) > 1:
                err=1
                if 'output' in locals():
                    output=output + ("Error! Cannot send REST request to:",url," check your request!")
                else:
                    output = ("Error! Cannot send REST request to:",url," check your request!")
            else:
                return jsonify("Error! Cannot send REST request to:",url," check your request!")

    if sendto == "rest4" or "rest4" in apis or apis == '' and current_app.config["USE_REST4"] == 'yes':
        if secondary:
            email2=getemail(duty1)
            email1=getemail(duty2)
            duty1=phone1
            duty2=phone2
        else:
            email1=getemail(duty1)
            email2=getemail(duty2)
            duty1=phone1
            duty2=phone2
        url=current_app.config["REST4_URL"]
        method=current_app.config["REST4_METHOD"]
        auth=current_app.config["REST4_AUTH"]
        user=current_app.config["REST4_USER"]
        password=current_app.config["REST4_PASSWORD"]
        arg1=current_app.config["REST4_ARG1"]
        arg2=current_app.config["REST4_ARG2"]
        arg3=current_app.config["REST4_ARG3"]
        arg4=current_app.config["REST4_ARG4"]
        try:
            result=send_rest1(duty1,duty2,project,email1,email2,url,method,auth,user,password,arg1,arg2,arg3,arg4)
            if len(apis) > 1:
                if 'output' in locals():
                    output=output + ("Send REST request to:",url," complete successfully")
                else:
                    output = ("Send REST request to:",url," complete successfully")
            else:
                return jsonify("Send REST request to:",url," complete successfully")
        except Exception as ex:
            print(ex)
            if len(apis) > 1:
                err=1
                if 'output' in locals():
                    output=output + ("Error! Cannot send REST request to:",url," check your request!")
                else:
                    output = ("Error! Cannot send REST request to:",url," check your request!")
            else:
                return jsonify("Error! Cannot send REST request to:",url," check your request!")


    if len(apis) > 1:
        if err == 1:
            return jsonify(output), 500
        else:
            return jsonify(output)


@app.route('/api/register/')
@authenticated
def registerapi():

    username = get_session_username(str(request.cookies.get(SESSION_ID)))
    tokens = db_session.query(Apikeys.user).filter(Apikeys.user==username).all()
    if tokens:
        return jsonify("token for user " + username +   " already exists")
    token=str(uuid4())
    hash_algoritm = hashlib.new("sha256")
    password_salt=current_app.config["PASSWORD_SALT"]
    hash_algoritm.update((token + password_salt).encode("UTF-8"))
    encoded = hash_algoritm.hexdigest()
    save_apitoken(username,encoded, new='true')

    return jsonify("Token for " + username + " created.","token: " + token)

@app.route('/api/update/')
@authenticated
def updateapi():
    username = get_session_username(str(request.cookies.get(SESSION_ID)))
    tokenid = (db_session.query(Apikeys.id).filter(Apikeys.user==username).first())[0]
    userapidata = db_session.query(Apikeys).filter(Apikeys.id==tokenid).first()

    if tokenid:
        token=str(uuid4())
        hash_algoritm = hashlib.new("sha256")
        password_salt=current_app.config["PASSWORD_SALT"]
        hash_algoritm.update((token + password_salt).encode("UTF-8"))
        encoded = hash_algoritm.hexdigest()
        update_apitoken(userapidata,username,encoded, tokenid)
        return jsonify("Token for " + username + " updated.","token: " + token)

@authenticated
def save_apitoken(username,shatoken, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    if new:
        newapi = Apikeys()
        newapi.user = username
        newapi.key = shatoken
        db_session.add(newapi)
    else:
        newapi.user = username
        newapi.key = shatoken
    # commit the data to the database
    db_session.commit()

@authenticated
def update_apitoken(userapidata,username,shatoken, tokenid):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    userapi = userapidata
    userapi.id = tokenid
    userapi.user = username
    userapi.key = shatoken
    userapi.date = db.func.now()
    
    # commit the data to the database
    db_session.commit()

@app.route('/api/check/<username>&<token>')
def checkapi(username,token):
    
    auth_result=auth_api(username,token)

    if auth_result is True:
        return jsonify("auth success!")
    else:
        abort(404)

def auth_api(username,token):
    try:

        tokenkey = (db_session.query(Apikeys.key).filter(Apikeys.user==username).first())[0]
        hash_algoritm = hashlib.new("sha256")
        password_salt=current_app.config["PASSWORD_SALT"]
        hash_algoritm.update((token + password_salt).encode("UTF-8"))
        encoded = hash_algoritm.hexdigest()
    except Exception:
        return False
    if encoded == tokenkey:
        return True
    else:
        return False   


@app.route('/reports/', defaults={'m': None, 'y': None}, methods=['GET', 'POST'])
@app.route('/reports/<m>&<y>', methods=['GET', 'POST'])
@authenticated
def getreports(m,y):
    
    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]
    if m:
        month = int(m)
        month = max(min(month, 12), 1)
        month_name = GregorianCalendar.MONTH_NAMES[month - 1]
    if y:
        year = int(y)

    if request.method == 'POST':
        date = request.form.get("date", "")
        fragments = re.split("-", date)
        try:
            month = int(fragments[1])
            month = max(min(month, 12), 1)
            month_name = GregorianCalendar.MONTH_NAMES[month - 1]
            year = int(fragments[0])
        except Exception:
            return jsonify("No reports found")

    calendar_id = current_app.config["DEFAULT_CALENDAR"]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    data = calendar_data.load_calendar(calendar_id)
    tasks = calendar_data.tasks_from_calendar(year, month, data)
    rtasks = calendar_data._repetitive_tasks_from_calendar(year, month, data)
    jsondata=json.loads(json.dumps(tasks))
    jsondata2=json.loads(json.dumps(rtasks))
    report=[]
    
    try:
        filterlist=str(current_month)
        
        if m:
            filterlist=m
        if request.method == 'POST':
            filterlist=str(month)
        found=jsondata[filterlist]

        
        for d in found:


            if len(found[str(d)]) > 1:
                same_duty=[]
                for duty1 in found[str(d)]:
                    same_duty.append(duty1['duty1'])
                
                if current_app.config["CALCULATE_EVERY_DAY"] == 'false':
                    same_duty=set(same_duty)

                for duty in same_duty:
                    report.append(duty)   
            else:
                for k in found[str(d)]:

                    report.append(k['duty1'])
                
                

        
    except Exception:
        False

    try:
        filterlist2=str(current_month)
        if m:
            filterlist2=m
        if request.method == 'POST':
            filterlist2=str(month)
        found2=jsondata2[filterlist2]
        
        for d in found2:

            for k in found2[str(d)]:

                if (calendar_data._is_repetition_hidden(data, str(k['id']), str(year), str(month)) ) is True:
                    False
                else:
                    report.append(k['duty1'])

    except Exception as e:
        False


    if not report:
        return jsonify("No reports found")
    
    alldutys=set(report)
    dutycount=len(alldutys)
    final_report={}
    for dt in alldutys:
        final_report[str(dt)]=report.count(str(dt))

    if m:
        return jsonify(final_report)

    return render_template('reports.html', report=final_report, month_name=month_name , year=year, get_duty_project=get_duty_project)



@app.route('/calendar_reports/', defaults={'m': None, 'y': None}, methods=['GET', 'POST'])
@app.route('/calendar_reports/<m>&<y>', methods=['GET', 'POST'])
@authenticated
def get_calendar_reports(m,y):
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
    return render_template('reports_full.html', days=month_days, dutys=dutys,check_calendar_duty=check_calendar_duty, year=y, mounth=m,month_name=month_name, get_duty_project=get_duty_project, get_day_of_week=get_day_of_week)

@app.route('/export/', defaults={'m': None, 'y': None}, methods=['GET', 'POST'])
@app.route('/export/<m>&<y>', methods=['GET', 'POST'])
@authenticated
def download_excel(m,y):
    excel_file = export_to_excel(m,y)
    return excel_file

@app.route('/api/call/<prj>/<username>&<token>', methods=['GET', 'POST'])
@authenticated
def get_current_duty(prj,username,token):
    today_duty = get_current_duty_api(prj,username,token)
    return today_duty    

@app.route('/remove_tasks/', defaults={'tasks': None}, methods=['GET', 'POST'])
@app.route('/remove_tasks/<tasks>', methods=['GET', 'POST'])
@authenticated
def remove_tasks(tasks):
    if request.method == 'POST':
        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = int(request.args.get("y", current_year))
        year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
        month = int(request.args.get("m", current_month))
        month = max(min(month, 12), 1)
        month_name = GregorianCalendar.MONTH_NAMES[month - 1]
        calendar_id = current_app.config["DEFAULT_CALENDAR"]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
        data = calendar_data.load_calendar(calendar_id)
        tasks = calendar_data.tasks_from_calendar(year, month, data)

        project = request.form.get("project", "")
        startdate = request.form.get("date", "")
        enddate = request.form.get("enddate", "")
        if startdate != enddate:
            from datetime import date, timedelta
            startdate_fragments = re.split("-", startdate)
            enddate_fragments = re.split("-", enddate)
            sdate = date(int(startdate_fragments[0]), int(startdate_fragments[1]), int(startdate_fragments[2]))   # start date
            edate = date(int(enddate_fragments[0]), int(enddate_fragments[1]), int(enddate_fragments[2]))   # end date
            delta = edate - sdate       # as timedelta
            for i in range(delta.days + 1):
                currentdate = re.split("-", str(sdate + timedelta(days=i)))
                day = int(currentdate[2])
                year = int(currentdate[0])  # type: Optional[int]
                month = int(currentdate[1])  # type: Optional[int]
                tsks=tasks[str(month)]
                for ts in tsks:
                    if day == int(ts):
                        for t in tsks[ts]:
                            jsondata=json.loads(json.dumps(t))
                            tskid=jsondata['id']
                            tskprj=jsondata['project']
                            if tskprj == project:
                                calendar_data.delete_task(calendar_id=calendar_id, year_str=str(year), month_str=str(month), day_str=str(day), task_id=int(tskid),)
           
        return render_template('remove.html')
    else:
        return render_template('remove.html')




start_scheduler(app)

if __name__ == "__main__":

    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])


