from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from .. import utils

endpoint = "/"


@mock.patch('reports.routes.database.get_connection')
def test_read_report_empty_list(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.return_value.read_paginated_documents = paginate
    paginate.return_value = {
        "count": 0,
        "previous": None,
        "next": None,
        "results": []
    }

    response = utils.client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == paginate.return_value


def test_read_report_list_fails_if_order_by_is_unknown():
    response = utils.client.get(endpoint, params={"order_by": "unknown"})
    assert response.status_code == 422


def test_read_report_list_fails_if_direction_is_unknown():
    response = utils.client.get(endpoint, params={"direction": 0})
    assert response.status_code == 422


def test_read_report_list_fails_if_page_is_less_than_one():
    response = utils.client.get(endpoint, params={"page": 0})
    assert response.status_code == 422


def test_read_report_list_fails_if_page_size_is_less_than_one():
    response = utils.client.get(endpoint, params={"page_size": 0})
    assert response.status_code == 422


@mock.patch('reports.routes.database.get_connection')
def test_read_report_list_fails_if_database_is_down(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.return_value.read_paginated_documents = paginate
    paginate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
