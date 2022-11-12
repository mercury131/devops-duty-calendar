import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dateutil import relativedelta


def test_reports_data():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%-m-%d')

    first_date=((datetime.today() ).strftime('%Y-%m-') + '1')
    end_date=((datetime.today() ).strftime('%Y-%m-' + '7'))

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    day=datetime.today().strftime('%d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%d')
    seven_day=(datetime.today()+ timedelta(days=7)).strftime('%-d')
    seven_day0=(datetime.today()+ timedelta(days=7)).strftime('%d')
    seven_month = (datetime.today() + timedelta(days=7)).strftime('%-m')

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create new duty task
    files = {
    'project': (None, 'test'),
    'duty1': (None, 'duty01'),
    'duty2': (None, 'duty02'),
    'date': (None, first_date),
    'enddate': (None, end_date),
    'is_all_day': (None, '1'),
    'start_time': (None, '00:00'),
    'end_time': (None, '00:00'),
    'repetition_value_weekday': (None, '0'),
    'repetition_value_monthday': (None, '1'),
    'repetition_value_monthday_end': (None, '1'),
    'repetition_value': (None, '0'),
    'details': (None, ''),
    'color': (None, '#3EB34F'),  
    }

    response = s.post((url + '/' + calendar + '/new_task'),files=files)

    # Making a get request to get reports
    response = s.get((url + '/reports/'))
    #print(response.content)

    assert "<tr><td>duty01 </td><td>7</td><td>test</td></tr>" in str(response.content)

#test_reports_data()