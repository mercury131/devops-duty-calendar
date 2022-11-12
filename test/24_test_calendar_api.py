import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
import json
from datetime import datetime, timedelta

def test_calendar_api():

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
    response = s.get((url + '/api/call/test/'  + user + '&' + token ))
    #print(response.content)

    assert response.status_code == 200

    assert '"Active_phone":"12345678901","Current_duty":"duty01","Project":"test","Secondary_duty":"duty02","Secondary_phone":"12345678901"' in str(response.content)

   

#test_calendar_api()