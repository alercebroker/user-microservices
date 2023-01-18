import json
from unittest import mock

from db_handler.models import Report
from pymongo import errors

from . import utils


@mock.patch('reports.database.get_connection')
def test_put_update_ignores_fields_not_defined_in_schema(mock_connection):
    oid = utils.random_oid()
    # Additional fields -> _id and date
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = report
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 200
    report = {k: v for k, v in report.items() if k not in {"_id", "date"}}
    update_one.assert_awaited_once_with(Report, {"_id": oid}, {"$set": report}, return_document=True)


@mock.patch('reports.database.get_connection')
def test_patch_update_ignores_fields_not_defined_in_schema(mock_connection):
    oid = utils.random_oid()
    # Additional fields -> _id and date
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = report
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.patch(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 200
    report = {k: v for k, v in report.items() if k not in {"_id", "date"}}
    update_one.assert_awaited_once_with(Report, {"_id": oid}, {"$set": report}, return_document=True)


@mock.patch('reports.database.get_connection')
def test_put_update_fails_if_missing_fields_defined_in_schema(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = report
    mock_connection.return_value.find_one_and_update = update_one

    report = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}

    response = utils.client.put(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 422


@mock.patch('reports.database.get_connection')
def test_patch_update_ignores_missing_fields_defined_in_schema(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = report
    mock_connection.return_value.find_one_and_update = update_one

    report = {k: v for k, v in report.items() if k not in {"_id", "date", "object"}}

    response = utils.client.patch(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 200
    update_one.assert_awaited_once_with(Report, {"_id": oid}, {"$set": report}, return_document=True)


@mock.patch('reports.database.get_connection')
def test_put_update_fails_if_missing_document(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = None
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 404


@mock.patch('reports.database.get_connection')
def test_patch_update_fails_if_missing_document(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.return_value = None
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.patch(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 404


@mock.patch('reports.database.get_connection')
def test_put_create_report_duplicate_fails(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.side_effect = errors.DuplicateKeyError(error="")
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.put(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400


@mock.patch('reports.database.get_connection')
def test_patch_create_report_duplicate_fails(mock_connection):
    oid = str(utils.random_oid())
    report = utils.report_factory()

    update_one = mock.AsyncMock()
    update_one.side_effect = errors.DuplicateKeyError(error="")
    mock_connection.return_value.find_one_and_update = update_one

    response = utils.client.patch(f"/{oid}", content=json.dumps(utils.json_converter(report)))
    assert response.status_code == 400
