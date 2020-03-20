import pytest
import requests_mock
from c20_server import document_download
from c20_server import reggov_api_doc_error

URL = "https://api.data.gov:443/regulations/v3/document.json?"
DOC_ID = "EPA-HQ-OAR-2011-0028-0108"
API_KEY = "12345"


def test_mock_response():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json='document received')
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response[0] == 'document received'


def test_incorrect_id_pattern():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=400)
        with pytest.raises(reggov_api_doc_error.IncorrectIDPatternException):
            bad_pattern = 'b4d' + DOC_ID + 'b4d'
            document_download.download_document(API_KEY, bad_pattern)


def test_incorrect_api_key():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=403)
        with pytest.raises(reggov_api_doc_error.IncorrectApiKeyException):
            document_download.download_document('INVALID', DOC_ID)


def test_bad_document_id():
    with requests_mock.Mocker() as mock:
        bad_id = DOC_ID + "-0101"
        mock.get(URL, json={'a': 'b'},
                 status_code=404)
        with pytest.raises(reggov_api_doc_error.BadDocIDException):
            document_download.download_document(API_KEY, bad_id)


def test_exceed_call_limit():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'a': 'b'},
                 status_code=429)
        with pytest.raises(reggov_api_doc_error.ExceedCallLimitException):
            document_download.download_document(API_KEY, DOC_ID)


def test_file_formats():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'fileFormats': ['file link']})
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response[1][0] == 'file link'


def test_multiple_file_formats():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'fileFormats': ['file link', 'file link2']})
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response[1][0] == 'file link'
        assert response[1][1] == 'file link2'


def test_attachments():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'attachments': [{'fileFormats': ['file link']}]})
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response[1][0] == 'file link'


def test_multiple_attachments():
    with requests_mock.Mocker() as mock:
        mock.get(URL, json={'attachments': [{'fileFormats': ['file link']}, {'fileFormats': ['file link2']}]})
        response = document_download.download_document(API_KEY, DOC_ID)
        assert response[1][1] == 'file link'
        assert response[1][2] == 'file link2'
