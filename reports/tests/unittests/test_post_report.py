import json
from datetime import datetime, timezone
from unittest import mock

from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

from reports.database import models
from .. import utils

report = utils.report_factory()
endpoint = "/"


@mock.patch('reports.database.models.PyObjectId')
@mock.patch('reports.database.models.datetime')
def test_report_model_creation_auto_fills_id_and_date(mock_datetime, mock_oid):
    mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0)
    mock_oid.return_value = utils.random_oid()

    new_report = models.Report(**{k: v for k, v in report.items() if k not in ("_id", "date")})
    assert new_report.id == mock_oid.return_value
    assert new_report.date == mock_datetime.now.return_value
    mock_oid.assert_called_once_with()
    mock_datetime.now.assert_called_once_with(timezone.utc)


@mock.patch('reports.database.models.datetime')
def test_now_utc_datetime_has_millisecond_resolution_and_strips_timezone(mock_datetime):
    mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0, 1234)
    date = models._utcnow()

    assert date == datetime(2023, 1, 1, 0, 0, 0, 1000)
    assert date.tzinfo is None
    mock_datetime.now.assert_called_once_with(timezone.utc)


@mock.patch('reports.routes.database.get_connection')
def test_post_report_ignores_fields_not_defined_in_schema(mock_connection):
    date = datetime(2023, 1, 1, 0, 0, 0)
    oid = utils.random_oid()
    # Additional fields -> _id and date

    create_document = mock.AsyncMock()
    mock_connection.return_value.create_document = create_document
    expected = report.copy()
    expected["_id"] = oid
    expected["date"] = date
    create_document.return_value = expected

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 201

    insert_dict = {k: v for k, v in expected.items() if k not in {"_id", "date"}}
    create_document.assert_awaited_once_with(models.Report, insert_dict)

    json_response = response.json()
    assert json_response == utils.json_converter(expected)


def test_post_report_fails_if_missing_fields_defined_in_schema():
    bad_input = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}
    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(bad_input)))
    assert response.status_code == 422


@mock.patch('reports.routes.database.get_connection')
def test_post_report_duplicate_fails(mock_connection):
    create_document = mock.AsyncMock()
    create_document.side_effect = DuplicateKeyError(error="")
    mock_connection.return_value.create_document = create_document

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400


@mock.patch('reports.routes.database.get_connection')
def test_post_report_fails_if_database_is_down(mock_connection):
    create_document = mock.AsyncMock()
    create_document.side_effect = ServerSelectionTimeoutError()
    mock_connection.return_value.create_document = create_document

    response = utils.client.post(endpoint, content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 503
