from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from . import utils

endpoint = "/"


@mock.patch('reports.database.get_connection')
def test_get_report_list_empty(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.return_value = []

    response = utils.client.get(endpoint)

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

    response = utils.client.get(endpoint)
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

    response = utils.client.get(endpoint, params={"page": page, "page_size": size})
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

    response = utils.client.get(endpoint, params={"page": page, "page_size": size})
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

    response = utils.client.get(endpoint, params={"page": page, "page_size": size})
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["count"] == n
    assert json_response["previous"] == page - 1
    assert json_response["next"] == page + 1
    assert json_response["results"] == utils.create_jsons(reports)


@mock.patch('reports.database.get_connection')
def test_read_report_list_fails_if_database_is_down(mock_connection):
    mock_connection.return_value.aggregate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
