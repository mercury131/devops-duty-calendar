import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create new duty task
    files = {
    'project': (None, 'test'),
    'duty1': (None, 'duty01'),
    'duty2': (None, 'duty02'),
    'date': (None, current_date),
    'enddate': (None, current_date),
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

    # Making a post request to create second duty task
    files = {
    'project': (None, 'test'),
    'duty1': (None, 'duty01'),
    'duty2': (None, 'duty02'),
    'date': (None, next_date),
    'enddate': (None, next_date),
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

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task'}))
    filtred_html['data-id'] = '12345'
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())

    expected_result=('<li class="task" data-day="' + day + '" data-id="12345" data-month="' + month + '" data-year="' + year + '" style="background-color:#3EB34F"> test duty01 12345678901 <p class="accordion-hidden"> duty02 12345678901 <a class="button smaller remove-task"' )

    assert expected_result in str(filtred_html)




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
    filtred_html['data-id'] = '12345'
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())
    expected_result=('<li class="task" data-day="' + next_day + '" data-id="12345" data-month="' + month + '" data-year="' + year + '" style="background-color:#3EB34F"> test duty01 12345678901 <p class="accordion-hidden"> duty02 12345678901 <a class="button smaller remove-task"' )

    assert expected_result in str(filtred_html)



def test_check_task_data():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    month0=datetime.today().strftime('%m')
    day=datetime.today().strftime('%-d')
    day0=datetime.today().strftime('%d')
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


    # Making a get request to get calendar task
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/' + year +  '/' + month + '/' + day + '/' + data_id ), headers=headers)    
    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('div', attrs={'class':'task-details-form'}))
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())

    expected_result=('<div class="task-details-form" id="task-details-form"><label for="text">Project</label><select class="select-css" id="projects" name="project" onclick="prj(); this.onclick=null;"><option selected="selected">test</option></select><br/><label for="text">Duty 1</label><select class="select-css" id="duty1" name="duty1"><option selected="selected">duty01</option></select><br/><label for="text">Duty 2</label><select class="select-css" id="duty2" name="duty2"><option selected="selected">duty02</option></select><br/><label for="date_picker">Start date</label><input id="date_picker" type="date" value="' + year + '-' + month0 + '-' + day0 + '"/><input id="date" name="date" type="hidden" value="' + year + '-' + month0 + '-' + day0 + '"/><br/><label for="date_picker2">End date</label><input id="date_picker2" type="date" value="' +  year + '-' + month0 + '-' + day0 + '"/><input id="enddate" name="enddate" type="hidden" value="'  + year + '-' + month0 + '-' + day0 + '"/><br/><label for="is_all_day">All day event</label><input checked="checked" id="is_all_day" name="is_all_day" type="checkbox" value="1"/><br/><div class="hidden" id="start_time_block"><label for="start_time">Start time</label><input id="start_time" name="start_time" type="time" value="00:00"/><br/><label for="end_time">End time</label><input id="end_time" name="end_time" type="time" value="00:00"/><br/></div><label for="repeats">Recurrent</label><input id="repeats" name="repeats" type="checkbox" value="1"/><div class="hidden" id="repetition_block"><input id="type_weekly" name="repetition_type" type="radio" value="w"/><label for="type_weekly">Occurs Weekly</label><input id="type_monthly" name="repetition_type" type="radio" value="m"/><label for="type_monthly">Occurs Monthly</label><br/><input id="subtype_weekly" name="repetition_subtype" type="radio" value="w"/><label for="subtype_weekly">Week day</label><input disabled="disabled" id="subtype_monthly" name="repetition_subtype" type="radio" value="m"/>')

    assert expected_result in str(filtred_html)




def test_check_second_task_data():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'

    current_date=datetime.today().strftime('%Y-%m-%d')

    next_date=(datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    year=datetime.today().strftime('%Y')
    month=datetime.today().strftime('%-m')
    month0=datetime.today().strftime('%m')
    day=datetime.today().strftime('%-d')
    next_day=(datetime.today()+ timedelta(days=1)).strftime('%-d')
    next_day0=(datetime.today()+ timedelta(days=1)).strftime('%d')

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a get request to get calendar tasks
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/?y=' + year +  '&m=' + month ), headers=headers)

    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('li', attrs={'class':'task', 'data-day': next_day}))
    #filtred_html['data-id'] = '12345'
    data_id=filtred_html['data-id']
    
    # Making a get request to get calendar task
    headers = {'Accept-Encoding': 'identity'}
    response = s.get((url + '/' + calendar + '/' + year +  '/' + month + '/' + next_day + '/' + data_id ), headers=headers)    
    parsed_html = BeautifulSoup(response.content, "lxml")
    filtred_html = (parsed_html.body.find('div', attrs={'class':'task-details-form'}))
    filtred_html = (str(filtred_html).replace('\n', ''))
    filtred_html = ' '.join(filtred_html.split())

    expected_result=('<div class="task-details-form" id="task-details-form"><label for="text">Project</label><select class="select-css" id="projects" name="project" onclick="prj(); this.onclick=null;"><option selected="selected">test</option></select><br/><label for="text">Duty 1</label><select class="select-css" id="duty1" name="duty1"><option selected="selected">duty01</option></select><br/><label for="text">Duty 2</label><select class="select-css" id="duty2" name="duty2"><option selected="selected">duty02</option></select><br/><label for="date_picker">Start date</label><input id="date_picker" type="date" value="' + year + '-' + month0 + '-' + next_day0 + '"/><input id="date" name="date" type="hidden" value="' + year + '-' + month0 + '-' + next_day0 + '"/><br/><label for="date_picker2">End date</label><input id="date_picker2" type="date" value="' +  year + '-' + month0 + '-' + next_day0 + '"/><input id="enddate" name="enddate" type="hidden" value="'  + year + '-' + month0 + '-' + next_day0 + '"/><br/><label for="is_all_day">All day event</label><input checked="checked" id="is_all_day" name="is_all_day" type="checkbox" value="1"/><br/><div class="hidden" id="start_time_block"><label for="start_time">Start time</label><input id="start_time" name="start_time" type="time" value="00:00"/><br/><label for="end_time">End time</label><input id="end_time" name="end_time" type="time" value="00:00"/><br/></div><label for="repeats">Recurrent</label><input id="repeats" name="repeats" type="checkbox" value="1"/><div class="hidden" id="repetition_block"><input id="type_weekly" name="repetition_type" type="radio" value="w"/><label for="type_weekly">Occurs Weekly</label><input id="type_monthly" name="repetition_type" type="radio" value="m"/><label for="type_monthly">Occurs Monthly</label><br/><input id="subtype_weekly" name="repetition_subtype" type="radio" value="w"/><label for="subtype_weekly">Week day</label><input disabled="disabled" id="subtype_monthly" name="repetition_subtype" type="radio" value="m"/>')
    print(expected_result)
    print(filtred_html)
    assert expected_result in str(filtred_html)


#test_add_task()
#test_check_second_task()
#test_check_task_data()
#test_check_second_task_data()