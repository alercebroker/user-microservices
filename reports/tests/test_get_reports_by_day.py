from datetime import date
from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from . import utils


endpoint = "/count_by_day"


@mock.patch('reports.database.get_connection')
def test_read_reports_grouped_by_day(mock_connection):
    results = [{'day': date(2023, 1, 1), 'count': 1}, {'day': date(2023, 1, 2), 'count': 2}]
    mock_connection.return_value.aggregate.return_value.__aiter__.return_value = results

    response = utils.client.get(endpoint)
    assert response.status_code == 200

    assert response.json() == utils.create_jsons(results)


@mock.patch('reports.database.get_connection')
def test_read_reports_grouped_by_day_fails_if_database_is_down(mock_connection):
    mock_connection.return_value.aggregate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503

