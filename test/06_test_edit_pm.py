import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_edit_pm():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to edit pm
    files = {
    'project': (None, 'test01'),
    'manager': (None, 'testpm'),
    'email': (None, 'pm@test.local'),  
    }

    s.post((url + '/pmitem/1'),files=files)

    # Making a get request to get pm
    response = s.get((url + '/pms'))
    print(response.content)

    assert "<tr><td>testpm</td><td>test01</td><td>pm@test.local</td><td>" in str(response.content)

#test_add_pm()