import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_delete_api_create():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)


    # Making a post request to create duty3
    files = {
    'name': (None, 'duty3'),
    'project': (None, 'test2'),
    'phone': (None, '12345678901'),
    'email': (None, 'duty3@test.local'),  
    }
    response = s.post((url + '/new_duty'),files=files)
    print(response)

    # Making a post request to create api mapping
    files = {
    'project': (None, 'test2'),
    'api': (None, 'telegram'),
    }

    s.post((url + '/add_api'),files=files)

    # Making a get request to get api mapping
    response = s.get((url + '/apisettings'))
    print(response.content)

    assert '<td>test2</td><td>telegram</td><td><a href="/apiitem/2">Edit</a></td><td><a href="/deleteapi/2">Delete</a></td>' in str(response.content)

def test_delete_api_remove():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a auth post request to remove api mapping
    response = s.post((url + '/deleteapi/2'))
    
    print(response)

    assert response.status_code == 200

def test_delete_api_check():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a get request to get pm
    response = s.get((url + '/apisettings'))
    print(response.content)

    assert '<td>test2</td><td>telegram</td><td><a href="/apiitem/2">Edit</a></td><td><a href="/deleteapi/2">Delete</a></td>' not in str(response.content)

#test_delete_api_create()
#test_delete_api_remove()
#test_delete_api_check()