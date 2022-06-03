import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)


    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-day': day}))
    data_id=filtred_html['data-id']



    # Making a request to delete duty task

    response = s.delete((url + '/' + calendar + '/' + year +  '/' + month + '/' + day + '/' + data_id))

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-day': next_day}))
    data_id=filtred_html['data-id']  
    print(data_id)
    # Making a  request to delete second duty task

    response = s.delete((url + '/' + calendar + '/' + year +  '/' + month + '/' + next_day + '/'  + data_id))

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task'}))
    print(filtred_html)
    if filtred_html is None:
        print('data-id not found')
    else:
        filtred_html['data-id'] = '12345'

    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())

    expected_result=('<li class="task" data-day="' + day + '" data-id="12345" data-month="' + month + '" data-year="' + year + '" style="background-color:#3EB34F"> test duty02 12345678901 <p class="accordion-hidden"> duty01 12345678901 <a class="button smaller remove-task"' )
    assert expected_result not in str(filtred_html)




def test_check_second_task():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    day=datetime.today().strftime('%-d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-day': next_day}))
    if filtred_html is not None:
        print('here')
        print(filtred_html)
        filtred_html['data-id'] = '12345'
        filtred_html = (str(filtred_html).replace('\n', ''))
        filtred_html = ' '.join(filtred_html.split())
    else:
        filtred_html= 'nothing'
    expected_result=('<li class="task" data-day="' + next_day + '" data-id="12345" data-month="' + month + '" data-year="' + year + '" style="background-color:#3EB34F"> test duty02 12345678901 <p class="accordion-hidden"> duty01 12345678901 <a class="button smaller remove-task"' )
    print(filtred_html)
    assert expected_result not in str(filtred_html)





#test_delete_task()
#test_check_second_task()
