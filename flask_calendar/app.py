#!/usr/bin/python

import locale
import os
from typing import Dict


from apscheduler.schedulers.background import BackgroundScheduler

import config  # noqa: F401
from flask import Flask, session, Response, send_from_directory, flash, render_template, request, redirect, jsonify
from flask_calendar.db_setup import init_db, db_session
from flask_sqlalchemy import SQLAlchemy
from flask_calendar.cache import cache
from flask_calendar.actions import (
    delete_task_action,
    do_login_action,
    edit_task_action,
    hide_repetition_task_instance_action,
    index_action,
    login_action,
    main_calendar_action,
    new_task_action,
    save_task_action,
    update_task_action,
    update_task_day_action,
)
from flask_calendar.app_utils import task_details_for_markup

#for test
from flask_htpasswd import HtPasswdAuth

def get_db(app):
    db = SQLAlchemy(app)
    return db


def create_app(config_overrides: Dict = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    app.secret_key = app.config["SECRET_KEY"]

    app.scheduler = BackgroundScheduler()
    app.scheduler.start()
    
    cache.init_app(app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': app.config["CACHE_DIR"],'CACHE_DEFAULT_TIMEOUT': 15})


    if app.config["USE_TEST_ROUTE"] == 'yes':
        # for test
        app.config['FLASK_HTPASSWD_PATH'] = '/home/darkwind/flask-calendar/.htpasswd'
        app.config['FLASK_SECRET'] = 'secure me!'
        htpasswd = HtPasswdAuth(app)

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon() -> Response:
        return send_from_directory(
            os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )
    
    if app.config["USE_TEST_ROUTE"] == 'yes':
        @app.route('/test/<PARAM1>&<PARAM2>@<PARAM3>&extension=<PARAM4>&context=<PARAM5>&timeout=<PARAM6>', methods=['GET', 'POST'])
        @htpasswd.required
        def test(PARAM1,PARAM2,PARAM3,PARAM4,PARAM5,PARAM6, *args, **kwargs):
            if request.method == 'POST':
                #
                return jsonify("method POST",PARAM1,PARAM2,PARAM3,PARAM4,PARAM5,PARAM6)
            else:
                return jsonify(PARAM1,PARAM2,PARAM3,PARAM4,PARAM5,PARAM6)

    if app.config["USE_TEST_ROUTE"] == 'yes':
        @app.route('/testsms/<PARAM1>text=<PARAM2>&provider=<PARAM3>&timeout=<PARAM4>', methods=['GET', 'POST'])
        @htpasswd.required
        def testsms(PARAM1,PARAM2,PARAM3,PARAM4, *args, **kwargs):
            if request.method == 'POST':
                #
                return jsonify("method POST",PARAM1,PARAM2,PARAM3,PARAM4)
            else:
                return jsonify(PARAM1,PARAM2,PARAM3,PARAM4)

    app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/task/<task_id>",
        "update_task_action",
        update_task_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action, methods=["DELETE"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/",
        "update_task_day_action",
        update_task_day_action,
        methods=["PUT"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/",
        "hide_repetition_task_instance_action",
        hide_repetition_task_instance_action,
        methods=["POST"],
    )
    

        

    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup

    return app

app = create_app()
db = SQLAlchemy(app)

