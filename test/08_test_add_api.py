import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_add_api():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a post request to create api mapping
    files = {
    'project': (None, 'test'),
    'api': (None, 'telegram'),
    }

    s.post((url + '/add_api'),files=files)

    # Making a get request to get api mapping
    response = s.get((url + '/apisettings'))
    print(response.content)

    assert '<td>test</td><td>telegram</td><td><a href="/apiitem/1">Edit</a></td><td><a href="/deleteapi/1">Delete</a></td>' in str(response.content)

#test_add_api()