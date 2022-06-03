import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dateutil import relativedelta

def test_add_task():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%-m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    day=datetime.today().strftime('%-d')
    day0=datetime.today().strftime('%d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')
    next_day0=(datetime.today()+ timedelta(days=1)).strftime('%d')
    dt = datetime.today()
    next_month = dt + relativedelta.relativedelta(months=1)
    next_month = next_month.strftime('%-m')
    print('next month',next_month)

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create new duty repeat task
    files = {
    'project': (None, 'test'),
    'duty1': (None, 'duty01'),
    'duty2': (None, 'duty02'),
    'date': (None, current_date),
    'enddate': (None, current_date),
    'is_all_day': (None, '1'),
    'start_time': (None, '00:00'),
    'end_time': (None, '00:00'),
    'repeats': (None, '1'),
    'repetition_type': (None, 'm'),
    'repetition_subtype': (None, 'm'),
    'repetition_value_weekday': (None, '0'),
    'repetition_value_monthday': (None, '1'),
    'repetition_value_monthday_end': (None, '1'),
    'repetition_value': (None, '1'),
    'details': (None, ''),
    'color': (None, '#3EB34F'),  
    }

    response = s.post((url + '/' + calendar + '/new_task'),files=files)

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + next_month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task'}))
    filtred_html['data-id'] = '12345'
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())
    day='1'
    expected_result=('<li class="task" data-day="' + day + '" data-id="12345" data-month="' + next_month + '" data-recurrent="1" data-year="' + year + '" style="background-color:#3EB34F"> test duty01 12345678901 <p class="accordion-hidden"> duty02 12345678901 <a class="button smaller remove-task"' )
    assert expected_result in str(filtred_html)


def test_delete_task():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%-m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    day=datetime.today().strftime('%-d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')
    dt = datetime.today()
    next_month = dt + relativedelta.relativedelta(months=1)
    next_month = next_month.strftime('%-m')

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-recurrent': '1'}))
    data_id=filtred_html['data-id']


    # Making a request to delete duty task

    response = s.delete((url + '/' + calendar + '/' + year +  '/' + month + '/' + day + '/' + data_id))

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task'}))
    print(filtred_html)
    if filtred_html is None:
        print('data-id not found')
        filtred_html='nothing'
    else:
        filtred_html = (str(filtred_html).replace('\n', ''))
        filtred_html = ' '.join(filtred_html.split())    
        filtred_html['data-id'] = '12345'
        filtred_html = (str(filtred_html).replace('\n', ''))
        filtred_html = ' '.join(filtred_html.split())
    day='1'
    expected_result=('<li class="task" data-day="' + day + '" data-id="12345" data-month="' + month + '" data-recurrent="1" data-year="' + year + '" style="background-color:#3EB34F"> test duty01 12345678901 <p class="accordion-hidden"> duty02 12345678901 <a class="button smaller remove-task"' )
    assert expected_result not in str(filtred_html)




#test_add_task()
#test_delete_task()