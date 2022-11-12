import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_add_pm():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create pm
    files = {
    'project': (None, 'test'),
    'manager': (None, 'testpm'),
    'email': (None, 'pm@test.local'),  
    }

    s.post((url + '/add_pm'),files=files)

    # Making a get request to get pm
    response = s.get((url + '/pms'))
    print(response.content)

    assert "<tr><td>testpm</td><td>test</td><td>pm@test.local</td><td>" in str(response.content)

#test_add_pm()