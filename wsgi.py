from flask_calendar.main import app


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
