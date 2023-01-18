import json
from unittest import mock

from db_handler.utils import PyObjectId
from db_handler.models import Report
from pymongo import errors

from . import utils


@mock.patch('reports.database.Report', autospec=True)
@mock.patch('reports.database.get_connection')
def test_create_report_ignores_body_id_and_date(mock_connection, mock_report):
    fixed_id = "123456789012345678901234"
    report = utils.report_factory()

    insert_one = mock.AsyncMock()
    insert_one.return_value.inserted_id = fixed_id
    mock_connection.return_value.insert_one = insert_one
    mock_report.side_effect = lambda **kwargs: Report(_id=PyObjectId(fixed_id), **kwargs)

    response = utils.client.post("/", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 201

    json_response = response.json()
    json_report = utils.json_converter(report)
    assert json_response["_id"] != json_report["_id"]
    assert json_response["date"] != json_report["date"]

    json_report.pop("_id")
    json_response.pop("_id")
    json_report.pop("date")
    json_response.pop("date")
    assert json_response == json_report


@mock.patch('reports.database.get_connection')
def test_create_report_duplicate_fails_with_status_400(mock_connection):
    report = utils.report_factory()

    insert_one = mock.AsyncMock()
    insert_one.side_effect = errors.DuplicateKeyError(error="")
    mock_connection.return_value.insert_one = insert_one
    # Will fail if _id is also present in kwargs (expected so that schema doesn't pass it)

    response = utils.client.post("/", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400
