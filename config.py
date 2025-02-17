import flask_calendar.constants as constants

DEBUG = False
DATA_FOLDER = "data"
USERS_DATA_FOLDER = "users"
BASE_URL = "http://0.0.0.0:5000"
MIN_YEAR = 2017
MAX_YEAR = 2200
PASSWORD_SALT = "something random and full of non-standard characters"
HOST_IP = "0.0.0.0"  # set to None for production
LOCALE = "en_US.UTF-8"
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "Europe/Moscow"

SQLALCHEMY_DATABASE_URI = 'sqlite:///duty.db'

SECRET_KEY = "justkey"

CACHE_DIR="/home/darkwind/flask-calendar/cache"

USE_LDAP = "true"
CACERT = '/home/darkwind/flask-ldap/ca_name.pem'
LDAPSERVER = "srv1.test.com"
OU = "dc=test,dc=com"
DOMAIN = "TEST.COM"
ALLOWGROUP_RO = "CN=duty-access-ro,CN=Users,DC=test,DC=com"
ALLOWGROUP_RW = "CN=duty-access,CN=Users,DC=test,DC=com"

DEFAULT_CALENDAR = "sample"

OWERWRITE_DETAILS = "yes"

CALCULATE_EVERY_DAY="false"

# Callback API Settings

USE_TEST_ROUTE = 'yes'

USE_TELEGRAM = 'no'
TELEGRAM_API_ID = ''
TELEGRAM_API_HASH = ''
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_MESSAGE = 'Alert Detected!'

USE_SLACK = 'no'
SLACK_APP_TOKEN= ''
SLACK_MESSAGE = 'Alert Detected!'

USE_EMAIL = 'no'
SMTP_SERVER = ''
SMTP_PORT = '587'
SMTP_LOGIN = ''
SMTP_PASSWORD = ''
SENDER_ADDRESS = ''
EMAIL_MESSAGE = 'Alert Detected!'
EMAIL_SUBJECT = 'Alert Detected!'

USE_REST1 = 'yes'
# <DUTY1> <DUTY2> <PROJECT> <EMAIL1> <EMAIL2> <ARG1> <ARG2> <ARG3> <ARG4>
REST1_URL = 'http://0.0.0.0:5000/test/<DUTY1>&<DUTY2>@out&extension=<ARG1>&context=play&timeout=900'
REST1_METHOD = 'POST'
REST1_AUTH = 'yes'
REST1_USER = 'admin'
REST1_PASSWORD = '12345'
REST1_ARG1 = 'hello-world'
REST1_ARG2 = ''
REST1_ARG3 = ''
REST1_ARG4 = ''

USE_REST2 = 'no'
# <DUTY1> <DUTY2> <PROJECT> <EMAIL1> <EMAIL2> <ARG1> <ARG2> <ARG3> <ARG4>
REST2_URL = 'http://'
REST2_METHOD = 'POST'
REST2_AUTH = ''
REST2_USER = ''
REST2_PASSWORD = ''
REST2_ARG1 = ''
REST2_ARG2 = ''
REST2_ARG3 = ''
REST2_ARG4 = ''


USE_REST3 = 'no'
# <DUTY1> <DUTY2> <PROJECT> <EMAIL1> <EMAIL2> <ARG1> <ARG2> <ARG3> <ARG4>
REST3_URL = 'http://'
REST3_METHOD = 'POST'
REST3_AUTH = ''
REST3_USER = ''
REST3_PASSWORD = ''
REST3_ARG1 = ''
REST3_ARG2 = ''
REST3_ARG3 = ''
REST3_ARG4 = ''


USE_REST4 = 'no'
# <DUTY1> <DUTY2> <PROJECT> <EMAIL1> <EMAIL2> <ARG1> <ARG2> <ARG3> <ARG4>
REST4_URL = 'http://'
REST4_METHOD = 'POST'
REST4_AUTH = ''
REST4_USER = ''
REST4_PASSWORD = ''
REST4_ARG1 = ''
REST4_ARG2 = ''
REST4_ARG3 = ''
REST4_ARG4 = ''

# Scheduler

JOBS = [
        {
            'id': 'notify project manager',
            'func': 'checkpm',
            'trigger': 'cron',
            'day': '*',
            'hour': 10,
            'minute': 10
        },
       {
           'id': 'notify duty',
           'func': 'check_duty_schedule',
            'trigger': 'cron',
            'day': '*',
            'hour': 11,
            'minute': 27
       },    
       {
           'id': 'Expire tokens',
           'func': 'check_token_ttl',
            'trigger': 'interval',
            'seconds': 86400
       },    
#   Example CRON usage
#        {
#            'id': 'notify pm',
#            'func': 'checkpm',
#            'trigger': 'cron',
#            'day': '*',
#            'hour': 11,
#            'minute': 27
#        },
#        {
#            'id': 'notify duty',
#            'func': 'check_duty_schedule',
#            'trigger': 'interval',
#            'seconds': 5
#        },    

    ]

# Scheduler SMTP Settings

# <PROJECT> variable used for duty current project

SH_SMTP_SERVER = ''
SH_SMTP_PORT = '587'
SH_SMTP_LOGIN = ''
SH_SMTP_PASSWORD = ''
SH_SENDER_ADDRESS = ''

SH_PM_EMAIL_MESSAGE = 'No duty in schedule calendar today! Check your schedule!'
SH_PM_EMAIL_SUBJECT = 'No duty in schedule calendar!'

SH_DUTY_EMAIL_MESSAGE = 'Your duty on the project <PROJECT> started today!'
SH_DUTY_EMAIL_SUBJECT = 'Your duty on the project <PROJECT> started today!'

SH_LAST_DUTY_EMAIL_MESSAGE = 'Your duty on the project <PROJECT> ended today!'
SH_LAST_DUTY_EMAIL_SUBJECT = 'Your duty on the project <PROJECT> ended today!'

SH_ADMINISTRATOR_EMAIL = ''

# Scheduler REST Settings

SH_USE_REST = 'no'
# <DUTY1> <DUTY2> <PROJECT> <EMAIL1> <EMAIL2> <ARG1> <ARG2> <ARG3> <ARG4>
SH_REST_URL1 = 'http://0.0.0.0:5000/testsms/<DUTY1>&text=<ARG1><PROJECT>&provider=sms&timeout=900'
SH_REST_URL2 = 'http://0.0.0.0:5000/testsms/<DUTY2>&text=<ARG2><PROJECT>&provider=sms&timeout=900'
SH_REST_METHOD = 'POST'
SH_REST_AUTH = 'yes'
SH_REST_USER = 'admin'
SH_REST_PASSWORD = '12345'
SH_REST_ARG1 = 'Your duty started today on the project-'
SH_REST_ARG2 = 'Your duty ended today on the project-'
SH_REST_ARG3 = ''
SH_REST_ARG4 = ''


WEEK_STARTING_DAY = constants.WEEK_START_DAY_MONDAY

MONTHS_TO_EXPORT = 6  # currently only used for ICS export

FEATURE_FLAG_ICAL_EXPORT = False

# (base ^ attempts ) second delays between failed logins
FAILED_LOGIN_DELAY_BASE = 2

# If true, will automatically decorate hyperlinks with <a> tags upon rendering them
AUTO_DECORATE_TASK_DETAILS_HYPERLINK = True

SHOW_VIEW_PAST_BUTTON = True

# Of use if SHOW_VIEW_PAST_BUTTON is False
HIDE_PAST_TASKS = False

# days past to keep hidden tasks (future ones always kept) counting all months as 31 days long
DAYS_PAST_TO_KEEP_HIDDEN_TASKS = 62

# Cookies config
COOKIE_HTTPS_ONLY = False
COOKIE_SAMESITE_POLICY = "Lax"

# If to render emoji buttons at the task create/edit page
EMOJIS_ENABLED = True

# Colors for new task buttons
BUTTON_CUSTOM_COLOR_VALUE = "#3EB34F"
BUTTONS_COLORS_LIST = (
    ("#FF4848", "Red"),
    ("#3EB34F", "Green"),
    ("#2966B8", "Blue"),
    ("#808080", "Grey"),
    ("#B05F3C", "Brown"),
    ("#9588EC", "Purple"),
    ("#F2981A", "Orange"),
    ("#3D3D3D", "Black"),
)
# Emojis for new task buttons
BUTTONS_EMOJIS_LIST = (
    "💬",
    "📞",
    "🍔",
    "🍺",
    "📽️",
    "🎂",
    "🏖️",
    "💻",
    "📔",
    "✂️",
    "🚂",
    "🏡",
    "🐶",
    "🐱",
)

# percent of chance to do a GC-like sweep on save and clean empty and/or past hidden entries.
# values [0, 100] -> Note that 0 disables it, 100 makes it run every time
GC_ON_SAVE_CHANCE = 30
