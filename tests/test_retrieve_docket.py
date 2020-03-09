"""
Test the retrieve_docket.py file
"""
import requests_mock
import pytest
from c20_server.retrieve_docket import get_docket
from c20_server import reggov_api_docket_error

URL = "https://api.data.gov:443/regulations/v3/docket.json?api_key="
API_KEY = "VALID KEY"
DOCKET_ID = "EPA-HQ-OAR-2011-0028"


def test_good_response():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&docketID=" + DOCKET_ID,
                 json='The test is successful')
        response = get_docket(API_KEY, DOCKET_ID)

        assert response == '"The test is successful"'


def test_bad_docket_id():
    with requests_mock.Mocker() as mock:
        bad_docket = DOCKET_ID + '-0101'
        mock.get(URL + API_KEY + "&docketID=" + bad_docket,
                 json='The test yields a bad id', status_code=404)

        with pytest.raises(reggov_api_docket_error.BadDocketID):
            get_docket(API_KEY, bad_docket)


def test_no_docket_id():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&docketID=",
                 json='The test yields a bad id', status_code=404)

        with pytest.raises(reggov_api_docket_error.BadDocketID):
            get_docket(API_KEY, '')


def test_bad_docket_id_pattern():
    with requests_mock.Mocker() as mock:
        bad_docket = 'b4d' + DOCKET_ID + 'b4d'
        mock.get(URL + API_KEY + "&docketID=" + bad_docket,
                 json='The test yields a bad id pattern', status_code=400)

        with pytest.raises(reggov_api_docket_error.IncorrectIDPattern):
            get_docket(API_KEY, bad_docket)

def test_bad_API_KEY():
    with requests_mock.Mocker() as mock:
        mock.get(URL + 'INVALID' + "&docketID=" + DOCKET_ID,
                 json='The test yields a bad api key', status_code=403)

        with pytest.raises(reggov_api_docket_error.IncorrectApiKey):
            get_docket('INVALID', DOCKET_ID)


def test_no_API_KEY():
    with requests_mock.Mocker() as mock:
        mock.get(URL + "&docketID=" + DOCKET_ID,
                 json='The test yields a bad api key', status_code=403)

        with pytest.raises(reggov_api_docket_error.IncorrectApiKey):
            get_docket('', DOCKET_ID)


def test_maxed_API_KEY():
    with requests_mock.Mocker() as mock:
        mock.get(URL + API_KEY + "&docketID=" + DOCKET_ID,
                 json='The test yields a overused api key', status_code=429)

        with pytest.raises(reggov_api_docket_error.ExceedCallLimit):
            get_docket(API_KEY, DOCKET_ID)
