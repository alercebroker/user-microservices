from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from .. import utils


endpoint = "/count_by_day"


@mock.patch('reports.routes.database.get_connection')
def test_read_report_by_day_empty_list(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.return_value.read_multiple_documents = paginate
    paginate.return_value = []

    response = utils.client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == paginate.return_value


def test_read_report_by_day_list_fails_if_order_by_is_unknown():
    response = utils.client.get(endpoint, params={"order_by": "unknown"})
    assert response.status_code == 422


def test_read_report_by_day_list_fails_if_direction_is_unknown():
    response = utils.client.get(endpoint, params={"direction": 0})
    assert response.status_code == 422


@mock.patch('reports.routes.database.get_connection')
def test_read_report_by_day_list_fails_if_database_is_down(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.return_value.read_multiple_documents = paginate
    paginate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
