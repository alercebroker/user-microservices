from unittest import mock

from db_handler import DocumentNotFound
from pymongo.errors import ServerSelectionTimeoutError

from reports.database.models import Report
from .. import utils


@mock.patch('reports.routes.database.get_connection')
def test_delete_report_success(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    delete_document = mock.AsyncMock()
    delete_document.return_value = report
    mock_connection.return_value.delete_document = delete_document

    response = utils.client.delete(f"/{oid}")
    assert response.status_code == 204
    delete_document.assert_awaited_once_with(Report, str(oid))


@mock.patch('reports.routes.database.get_connection')
def test_delete_report_fails_if_missing_document(mock_connection):
    oid = utils.random_oid()

    delete_document = mock.AsyncMock()
    delete_document.side_effect = DocumentNotFound(str(oid))
    mock_connection.return_value.delete_document = delete_document

    response = utils.client.delete(f"/{oid}")
    assert response.status_code == 404


@mock.patch('reports.routes.database.get_connection')
def test_delete_report_fails_if_database_is_down(mock_connection):
    oid = utils.random_oid()

    delete_document = mock.AsyncMock()
    delete_document.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.delete_document = delete_document

    response = utils.client.delete(f"/{oid}")
    assert response.status_code == 503
