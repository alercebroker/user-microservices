from unittest import mock

from db_handler import DocumentNotFound
from pymongo.errors import ServerSelectionTimeoutError

from reports.database.models import Report
from .. import utils

oid = utils.random_oid()
report = utils.report_factory(_id=oid)
endpoint = f"/{oid}"

connection = 'reports.routes.db'


@mock.patch(connection)
def test_read_report_success(mock_connection):
    read_document = mock.AsyncMock()
    read_document.return_value = report
    mock_connection.read_document = read_document

    response = utils.client.get(endpoint)
    assert response.status_code == 200
    read_document.assert_awaited_once_with(Report, str(oid))


@mock.patch(connection)
def test_read_report_fails_if_missing_document(mock_connection):
    read_document = mock.AsyncMock()
    read_document.side_effect = DocumentNotFound(str(oid))
    mock_connection.read_document = read_document

    response = utils.client.get(endpoint)
    assert response.status_code == 404


@mock.patch(connection)
def test_read_report_fails_if_database_is_down(mock_connection):
    read_document = mock.AsyncMock()
    read_document.side_effect = ServerSelectionTimeoutError()
    mock_connection.read_document = read_document

    response = utils.client.get(endpoint)
    assert response.status_code == 503
