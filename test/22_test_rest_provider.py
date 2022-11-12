import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
import json
from datetime import datetime, timedelta

def test_rest_provider():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'


    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)


    # Making a get request to update token
    response = s.get((url + '/api/update/'))
    token=(((response.json())[1]).split(':')[1]).strip ()
    #print(response.status_code)
    #print(response.content)
    #print(token)

    # Making a get request to call rest provider
    response = s.get((url + '/call/test/'  + user + '&' + token))
    #print(response.status_code)
    #print(response.content)

    assert response.status_code == 500

    assert 'No duty found for' in str(response.content)



    current_date=datetime.today().strftime('%Y-%-m-%d')

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

    # Making a get request to call rest provider
    response = s.get((url + '/call/test/'  + user + '&' + token))
    #print(response.status_code)
    #print(response.content)

    assert response.status_code == 200

    assert 'Send REST request to:","http://0.0.0.0:5000/test/<DUTY1>&<DUTY2>@out&extension=<ARG1>&context=play&timeout=900"," complete successfully' in str(response.content)

    # Making a post request to call rest provider
    response = s.post((url + '/call/test/'  + user + '&' + token))
    #print(response.status_code)
    #print(response.content)

    assert response.status_code == 200

    assert 'Send REST request to:","http://0.0.0.0:5000/test/<DUTY1>&<DUTY2>@out&extension=<ARG1>&context=play&timeout=900"," complete successfully' in str(response.content)


    response_check = s.get((url + '/api/check/' + user + '&' + token))
    #print(response_check.status_code)
    #print(response_check.content)

    assert response_check.status_code == 200

    assert 'auth success!' in str(response_check.content)

#test_rest_provider()