import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dateutil import relativedelta

def test_delete_tasks():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%-m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    seven_date=(datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    day=datetime.today().strftime('%-d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')
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
    'date': (None, current_date),
    'enddate': (None, seven_date),  
    }


    response = s.post((url + '/remove_tasks'),files=files)

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + seven_month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-day': seven_day}))
    #filtred_html['data-id'] = '12345'
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())
    expected_result=('<li class="task" data-day="' + seven_day + '" data-id="12345" data-month="' + seven_month + '" data-year="' + year + '" style="background-color:#3EB34F"> test duty01 12345678901 <p class="accordion-hidden"> duty02 12345678901 <a class="button smaller remove-task"' )
    
    assert expected_result not in str(filtred_html)



#test_delete_tasks()
