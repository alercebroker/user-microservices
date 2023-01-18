from datetime import date, datetime
from unittest import mock

from db_handler.models import Report

from . import utils


@mock.patch('reports.database.get_connection')
def test_get_report_list_empty(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.return_value = []

    response = utils.client.get("/")

    assert response.status_code == 200

    json = response.json()
    assert json["count"] == 0
    assert json["previous"] is None
    assert json["next"] is None
    assert json["results"] == []


@mock.patch('reports.database.get_connection')
def test_get_report_list_with_elements(mock_connection):
    n = 2
    reports = utils.create_reports(n)

    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": n}], reports

    response = utils.client.get("/")
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == n
    assert json_response["previous"] is None
    assert json_response["next"] is None
    assert json_response["results"] == utils.create_jsons(reports)


@mock.patch('reports.database.get_connection')
def test_get_report_list_paginated_with_next(mock_connection):
    n, size = 6, 2
    page = 1
    reports = utils.create_reports(size)

    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": n}], reports

    response = utils.client.get("/", params={"page": page, "page_size": size})
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == n
    assert json_response["previous"] is None
    assert json_response["next"] == page + 1
    assert json_response["results"] == utils.create_jsons(reports)


@mock.patch('reports.database.get_connection')
def test_get_report_list_paginated_with_previous(mock_connection):
    n, size = 6, 2
    page = n // size + (1 if n % size else 0)
    reports = utils.create_reports(size)

    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": n}], reports

    response = utils.client.get("/", params={"page": page, "page_size": size})
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == n
    assert json_response["previous"] == page - 1
    assert json_response["next"] is None
    assert json_response["results"] == utils.create_jsons(reports)


@mock.patch('reports.database.get_connection')
def test_get_report_list_paginated_with_previous_and_next(mock_connection):
    n, size = 6, 2
    page = n // size - 1 + (1 if n % size else 0)
    reports = utils.create_reports(size)

    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": n}], reports

    response = utils.client.get("/", params={"page": page, "page_size": size})
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == n
    assert json_response["previous"] == page - 1
    assert json_response["next"] == page + 1
    assert json_response["results"] == utils.create_jsons(reports)


@mock.patch('reports.database.get_connection')
def test_read_report_success(mock_connection):
    oid = utils.random_oid()
    report = utils.report_factory()

    find_one = mock.AsyncMock()
    find_one.return_value = report
    mock_connection.return_value.find_one = find_one

    response = utils.client.get(f"/{oid}")
    assert response.status_code == 200
    find_one.assert_awaited_once_with(Report, {"_id": oid})


@mock.patch('reports.database.get_connection')
def test_read_report_fails_if_missing_document(mock_connection):
    oid = utils.random_oid()

    find_one = mock.AsyncMock()
    find_one.return_value = None
    mock_connection.return_value.find_one = find_one

    response = utils.client.get(f"/{oid}")
    assert response.status_code == 404


@mock.patch('reports.database.get_connection')
def test_read_reports_grouped_by_day(mock_connection):
    results = [{'day': date(2023, 1, 1), 'count': 1}, {'day': date(2023, 1, 2), 'count': 2}]
    mock_connection.return_value.aggregate.return_value.__aiter__.return_value = results

    response = utils.client.get(f"/count_by_day")
    assert response.status_code == 200

    results = [{k: v.isoformat() if isinstance(v, date) else v for k, v in item.items()} for item in results]
    assert response.json() == results


@mock.patch('reports.database.get_connection')
def test_get_object_list(mock_connection):
    objects = [{
        "object": "object",
        "first_date": datetime(2023, 1, 1, 0, 0, 0),
        "last_date": datetime(2023, 1, 1, 0, 0, 0),
        "count": 1,
        "source": ["source"],
        "report_type": ["report_type"],
        "users": ["user"]
    }]

    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": 1}], objects

    response = utils.client.get("/by_object")
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == 1
    assert json_response["previous"] is None
    assert json_response["next"] is None
    assert json_response["results"] == utils.create_jsons(objects)
