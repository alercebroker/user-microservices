import json
from unittest import mock

from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

from reports.models import Report
from . import utils

oid = utils.random_oid()
report = utils.report_factory()
endpoint = f"/{oid}"


@mock.patch('reports.database.get_connection')
def test_put_ignores_fields_not_defined_in_schema(mock_connection):
    update_one = mock.AsyncMock()
    update_one.return_value = report
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 200
    # Additional fields -> _id and date
    to_modify = {k: v for k, v in report.items() if k not in {"_id", "date"}}
    update_one.assert_awaited_once_with(Report, {"_id": oid}, {"$set": to_modify}, return_document=True)


def test_put_fails_if_missing_fields_defined_in_schema():
    bad_input = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}
    response = utils.client.put(endpoint, content=json.dumps(utils.json_converter(bad_input)))
    assert response.status_code == 422


@mock.patch('reports.database.get_connection')
def test_put_fails_if_missing_document(mock_connection):
    update_one = mock.AsyncMock()
    update_one.return_value = None
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 404


@mock.patch('reports.database.get_connection')
def test_put_report_duplicate_fails(mock_connection):
    update_one = mock.AsyncMock()
    update_one.side_effect = DuplicateKeyError(error="")
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400


@mock.patch('reports.database.get_connection')
def test_put_report_fails_if_database_is_down(mock_connection):
    update_one = mock.AsyncMock()
    update_one.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 503
