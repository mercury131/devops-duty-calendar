import os
import requests
from requests.auth import HTTPBasicAuth
import pytest
from bs4 import BeautifulSoup


def test_reports_data_full():

    url='http://0.0.0.0:5000'

    user='testuser'
    password='TE$tP@ss123'

    calendar='sample'


    s = requests.Session()
    # Making a auth post request
    payload = {'username':user,'password':password}
    s.post((url + '/do_login'),data=payload)


    # Making a get request to get reports
    response = s.get((url + '/calendar_reports/'))
    #print(response.content)

    assert '<tr><td>duty01 </td><td>test</td><td>X</td><td>X</td><td>X</td><td>X</td><td>X</td><td>X</td><td>X</td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td>7</td></tr>' in str(response.content)

    assert '<tr><td>duty02 </td><td>test</td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td>0</td></tr>' in str(response.content)

    assert '<tr><td>duty3 </td><td>test2</td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td> </td><td>0</td></tr>' in str(response.content)

#test_reports_data_full()