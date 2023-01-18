from datetime import datetime
from unittest import mock

from fastapi.testclient import TestClient

from reports.main import app


client = TestClient(app)


mock_report_1 = {
    "_id": "1",
    "date": datetime(2023, 1, 1, 0, 0, 0),
    "object": "object",
    "solved": False,
    "source": "source",
    "observation": "observation",
    "report_type": "report_type",
    "owner": "owner"
}


mock_report_2 = {
    "_id": "2",
    "date": datetime(2023, 1, 1, 0, 0, 0),
    "object": "object",
    "solved": False,
    "source": "source",
    "observation": "observation",
    "report_type": "report_type",
    "owner": "owner"
}


def _report_as_json(report):
    return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in report.items()}


@mock.patch('reports.database.get_connection')
def test_get_report_list_empty(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.return_value = []
    response = client.get("/")
    assert response.status_code == 200
    json = response.json()
    assert json["count"] == 0
    assert json["previous"] is None
    assert json["next"] is None
    assert json["results"] == []


@mock.patch('reports.database.get_connection')
def test_get_report_list_with_elements(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": 2}], [mock_report_1, mock_report_2]
    response = client.get("/")
    assert response.status_code == 200
    json = response.json()
    assert json["count"] == 2
    assert json["previous"] is None
    assert json["next"] is None
    assert json["results"] == [_report_as_json(mock_report_1), _report_as_json(mock_report_2)]


@mock.patch('reports.database.get_connection')
def test_get_report_list_paginated_with_next(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": 2}], [mock_report_1]
    response = client.get("/", params={"page": 1, "page_size": 1})
    assert response.status_code == 200
    json = response.json()
    assert json["count"] == 2
    assert json["previous"] is None
    assert json["next"] == 2
    assert json["results"] == [_report_as_json(mock_report_1)]


@mock.patch('reports.database.get_connection')
def test_get_report_list_paginated_with_previous(mock_connection):
    cursor_to_list = mock.AsyncMock()
    mock_connection.return_value.aggregate.return_value.to_list = cursor_to_list
    cursor_to_list.side_effect = [{"total": 2}], [mock_report_2]
    response = client.get("/", params={"page": 2, "page_size": 1})
    assert response.status_code == 200
    json = response.json()
    assert json["count"] == 2
    assert json["previous"] == 1
    assert json["next"] is None
    assert json["results"] == [_report_as_json(mock_report_2)]
