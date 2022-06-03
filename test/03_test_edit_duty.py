import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_edit_duty():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to edit duty1
    files = {
    'name': (None, 'duty01'),
    'project': (None, 'test'),
    'phone': (None, '12345678901'),
    'email': (None, 'duty1@test.local'),  
    }
    response = s.post((url + '/item/1'),files=files)
    print(response)

    # Making a post request to create duty2
    files = {
    'name': (None, 'duty02'),
    'project': (None, 'test'),
    'phone': (None, '12345678901'),
    'email': (None, 'duty2@test.local'),  
    }
    response = s.post((url + '/item/2'),files=files)
    print(response)

    # Making a get request to get dutys
    response = s.get((url + '/duty_choice/test'))
    print(response.json())

    # print request object
    print(response)
    true_result="{'DUTY': ['duty01', 'duty02']}"
    assert str(response.json()) == true_result


#test_add_duty()