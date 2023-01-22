import json
from datetime import datetime
from unittest import mock

from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

from reports.database import Report
from reports.schemas import ReportIn
from .. import utils

report = utils.report_factory()
endpoint = "/"


@mock.patch('reports.routes.database.get_connection')
def test_create_report_ignores_fields_not_defined_in_schema(mock_connection):
    date = datetime(2023, 1, 1, 0, 0, 0)
    oid = utils.random_oid()
    # Additional fields -> _id and date

    create_document = mock.AsyncMock()
    mock_connection.return_value.create_document = create_document
    expected_output = report.copy()
    expected_output["_id"] = oid
    expected_output["date"] = date
    create_document.return_value = expected_output

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 201

    create_document.assert_awaited_once_with(Report, ReportIn(**expected_output))

    json_response = response.json()
    assert json_response == utils.json_converter(expected_output)


def test_create_report_fails_if_missing_fields_defined_in_schema():
    bad_input = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}
    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(bad_input)))
    assert response.status_code == 422


@mock.patch('reports.routes.database.get_connection')
def test_create_report_duplicate_fails(mock_connection):
    create_document = mock.AsyncMock()
    create_document.side_effect = DuplicateKeyError(error="")
    mock_connection.return_value.create_document = create_document

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400


@mock.patch('reports.routes.database.get_connection')
def test_create_report_fails_if_database_is_down(mock_connection):
    create_document = mock.AsyncMock()
    create_document.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.create_document = create_document

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 503
