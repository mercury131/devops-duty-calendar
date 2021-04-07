from flask_calendar.app import app
from flask_calendar.db_setup import init_db, db_session
from flask_calendar.forms import SearchForm, Duty
from flask import flash, current_app, session, render_template, request, redirect, jsonify
from flask_calendar.models import Project
from flask_calendar.tables import Results
from flask_calendar.app_utils import remove_session , get_session_username
from flask_calendar.constants import SESSION_ID
from flask_calendar.authentication import Authentication
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.call_providers import send_to_telegram, send_to_slack, send_email
import json
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
        #duty.name = "HELLO"
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
        # Add the new album to the database
        db_session.add(duty)
    else:
        #duty = Project()
        duty.name = form.name.data
        #duty.name = "HELLO"
        duty.project = form.project.data
        duty.phone = form.phone.data
        duty.email = form.email.data
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
    prj=value
    dutys = db_session.query(Project.name).filter(Project.project==prj).all()
    dutys = [item[0] for item in dutys]
    return jsonify({'DUTY': dutys})

@app.route('/duty_choice2/<value1>&<value2>')
def duty_choice2(value1,value2):
    prj=value1
    duty=value2
    dutys = db_session.query(Project.name).filter(Project.project==prj).all()
    dutys = [item[0] for item in dutys]
    dutys.append(dutys.pop(dutys.index(duty)))
    return jsonify({'DUTY': dutys})

@app.route('/duty_projects/')
def duty_projects():
    projects = db_session.query(Project.project).all()
    projects = [item[0] for item in projects]
    projects =list(set(projects))
    return jsonify({'PROJECTS': projects})

@app.route('/logout/')
@authenticated
def logout():
    #session.clear()
    session_id = request.cookies.get(SESSION_ID)
    username=get_session_username(session_id)
    print(username)
    remove_session(session_id,username)
    return redirect('/login')

@app.route('/call/<prj>')
def call(prj):
    project=prj
    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    #month_name = GregorianCalendar.MONTH_NAMES[month - 1]
    calendar_id = current_app.config["DEFAULT_CALENDAR"]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    data = calendar_data.load_calendar(calendar_id)
    tasks = calendar_data.tasks_from_calendar(year, month, data)
    jsondata=json.loads(json.dumps(tasks))
    for key in jsondata:
        filterlist=key

    found=list(filter(lambda x:x["project"]==project,jsondata[filterlist][str(current_day)]))
    if len(found) > 1:
        for x in found:
            duty1=x['duty1']
            duty2=x['duty2']
    else:
        duty1=found[0]['duty1']
        duty2=found[0]['duty2']

    phone1=getphone(duty1)
    phone2=getphone(duty2)
    if current_app.config["USE_TELEGRAM"] == 'yes':
        phone = '+' + phone1
        message=current_app.config["TELEGRAM_MESSAGE"] + " Project: " + project
        api_id=current_app.config["TELEGRAM_API_ID"]
        api_hash=current_app.config["TELEGRAM_API_HASH"]
        token=current_app.config["TELEGRAM_BOT_TOKEN"]
        try:
            send_to_telegram(phone,message,api_id,api_hash,token)
            return jsonify("Send message to:",phone1,"complete successfully")
        except Exception:
            return jsonify("Error while sending message to:",phone1,"detected","Check Telegram tokens or phone number format"), 500
    
    if current_app.config["USE_SLACK"] == 'yes':
        duty = duty1
        message = current_app.config["SLACK_MESSAGE"]
        slackchannel=project
        apitoken=current_app.config["SLACK_APP_TOKEN"]
        try:
            send_to_slack(duty,message,slackchannel,apitoken)
            return jsonify("Send message to:",duty,(" in slack cnannel #" + project + " complete successfully"))
        except Exception:
            return jsonify("Error while sending message to:",duty,"detected","Check Slack tokens or userID format"), 500

    if current_app.config["USE_EMAIL"] == 'yes':
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
                return jsonify("Send email message to:",email1," complete successfully")
            except Exception as ex:
                print(ex)
                return jsonify("Error while sending email message to:",email1,"detected","Check SMTP server settings"), 500
        else:
            #
            try:
                send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address,smtp_login=smtp_server_login,smtp_password=smtp_server_password)
                return jsonify("Send email message to:",email1," complete successfully")
            except Exception as ex:
                print(ex)
                return jsonify("Error while sending email message to:",email1,"detected","Check SMTP server settings"), 500








if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])