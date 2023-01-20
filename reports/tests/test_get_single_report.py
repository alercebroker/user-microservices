from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from reports.database import Report
from . import utils

oid = utils.random_oid()
report = utils.report_factory(_id=oid)
endpoint = f"/{oid}"


@mock.patch('reports.database._interactions.get_connection')
def test_read_report_success(mock_connection):
    find_one = mock.AsyncMock()
    find_one.return_value = report
    mock_connection.return_value.find_one = find_one

    response = utils.client.get(endpoint)
    assert response.status_code == 200
    find_one.assert_awaited_once_with(Report, {"_id": oid})


@mock.patch('reports.database._interactions.get_connection')
def test_read_report_fails_if_missing_document(mock_connection):
    find_one = mock.AsyncMock()
    find_one.return_value = None
    mock_connection.return_value.find_one = find_one

    response = utils.client.get(endpoint)
    assert response.status_code == 404


@mock.patch('reports.database._interactions.get_connection')
def test_read_report_fails_if_database_is_down(mock_connection):
    find_one = mock.AsyncMock()
    find_one.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.find_one = find_one

    response = utils.client.get(endpoint)
    assert response.status_code == 503
