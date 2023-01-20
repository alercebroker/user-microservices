import json
from datetime import datetime
from unittest import mock

from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

from reports.models import Report
from . import utils

report = utils.report_factory()
endpoint = "/"


@mock.patch('reports.models._reports.PyObjectId')
@mock.patch('reports.models._reports.datetime')
@mock.patch('reports.database.get_connection')
def test_create_report_ignores_fields_not_defined_in_schema(mock_connection, mock_datetime, mock_oid):
    date = datetime(2023, 1, 1, 0, 0, 0)
    oid = utils.random_oid()
    # Additional fields -> _id and date

    insert_one = mock.AsyncMock()
    mock_connection.return_value.insert_one = insert_one
    mock_datetime.utcnow.return_value = date
    mock_oid.return_value = oid

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 201

    report.update({"_id": oid, "date": date})
    insert_one.assert_awaited_once_with(Report, report)

    json_response = response.json()
    assert json_response == utils.json_converter(report)


def test_create_report_fails_if_missing_fields_defined_in_schema():
    bad_input = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}
    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(bad_input)))
    assert response.status_code == 422


@mock.patch('reports.database.get_connection')
def test_create_report_duplicate_fails(mock_connection):
    insert_one = mock.AsyncMock()
    insert_one.side_effect = DuplicateKeyError(error="")
    mock_connection.return_value.insert_one = insert_one

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400


@mock.patch('reports.database.get_connection')
def test_create_report_fails_if_database_is_down(mock_connection):
    insert_one = mock.AsyncMock()
    insert_one.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.insert_one = insert_one

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 503
