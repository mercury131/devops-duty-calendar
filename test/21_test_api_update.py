import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
import json

def test_api_update():

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

    assert response.status_code == 200

    assert 'Token for testuser updated.","token:' in str(response.content)

    
    response_check = s.get((url + '/api/check/' + user + '&' + token))
    #print(response_check.status_code)
    #print(response_check.content)

    assert response_check.status_code == 200

    assert 'auth success!' in str(response_check.content)

#test_api_update()