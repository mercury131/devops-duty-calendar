import os
import requests
from requests.auth import HTTPBasicAuth
import pytest



def test_reports_nodata():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)


    # Making a get request to get reports
    response = s.get((url + '/reports/'))
    print(response.json())

    true_result="No reports found"
    assert str(response.json()) == true_result

test_reports_nodata()