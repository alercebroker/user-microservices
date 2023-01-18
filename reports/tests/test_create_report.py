import json
from datetime import datetime
from unittest import mock

from db_handler.models import Report
from pymongo import errors

from . import utils


@mock.patch('db_handler.utils.PyObjectId')
@mock.patch('db_handler.models.datetime')
@mock.patch('reports.database.get_connection')
def test_create_report_ignores_fields_not_defined_in_schema(mock_connection, mock_datetime, mock_oid):
    date = datetime(2023, 1, 1, 0, 0, 0)
    oid = utils.random_oid()
    # Additional fields -> _id and date
    report = utils.report_factory()

    insert_one = mock.AsyncMock()
    mock_connection.return_value.insert_one = insert_one
    mock_datetime.utcnow.return_value = date
    mock_oid.return_value = oid

    response = utils.client.post("/", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 201

    report.update({"_id": oid, "date": date})
    insert_one.assert_awaited_once_with(Report, report)

    json_response = response.json()
    assert json_response == utils.json_converter(report)


@mock.patch('reports.database.get_connection')
def test_create_report_duplicate_fails(mock_connection):
    report = utils.report_factory()

    insert_one = mock.AsyncMock()
    insert_one.side_effect = errors.DuplicateKeyError(error="")
    mock_connection.return_value.insert_one = insert_one

    response = utils.client.post("/", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400
