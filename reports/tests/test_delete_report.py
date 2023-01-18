from unittest import mock

from db_handler.models import Report

from . import utils


@mock.patch('reports.database.get_connection')
def test_delete_report_success(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    delete_one = mock.AsyncMock()
    delete_one.return_value = report
    mock_connection.return_value.find_one_and_delete = delete_one

    response = utils.client.delete(f"/{oid}")
    assert response.status_code == 204
    delete_one.assert_awaited_once_with(Report, {"_id": oid})


@mock.patch('reports.database.get_connection')
def test_delete_report_fails_if_missing_document(mock_connection):
    oid = utils.random_oid()

    delete_one = mock.AsyncMock()
    delete_one.return_value = None
    mock_connection.return_value.find_one_and_delete = delete_one

    response = utils.client.delete(f"/{oid}")
    assert response.status_code == 404
