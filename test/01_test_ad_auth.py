import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_ad_auth():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)

    # Making a get request to get projects
    response = s.get((url + '/duty_projects/'))
    print(response.json())

    # print request object
    print(response)
    true_result="{'PROJECTS': ['Select project']}"
    assert str(response.json()) == true_result


#test_ad_auth()