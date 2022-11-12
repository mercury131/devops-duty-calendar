import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_delete_duty_create():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create duty3
    files = {
    'name': (None, 'duty03'),
    'project': (None, 'test'),
    'phone': (None, '12345678901'),
    'email': (None, 'duty3@test.local'),  
    }
    response = s.post((url + '/new_duty'),files=files)
    print(response)

    # Making a get request to get dutys
    response = s.get((url + '/duty_choice/test'))
    print(response.json())

    # print request object
    print(response)
    true_result="{'DUTY': ['duty01', 'duty02', 'duty03']}"
    assert str(response.json()) == true_result

def test_delete_duty_remove():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to delete duty3

    response = s.post((url + '/delete/3'))
    print(response)

    # Making a get request to get dutys
    response = s.get((url + '/duty_choice/test'))
    print(response.json())

    # print request object
    print(response)
    true_result="{'DUTY': ['duty01', 'duty02']}"
    assert str(response.json()) == true_result

#test_delete_duty_create()
#test_delete_duty_remove()