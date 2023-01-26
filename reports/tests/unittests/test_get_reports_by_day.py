from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from reports.filters import QueryByDay
from .. import utils


endpoint = "/count_by_day"

connection = 'reports.routes.db'


def test_query_pipeline_includes_grouping_by_day_stage():
    pipeline = QueryByDay().pipeline()

    assert "$sort" in pipeline[-1]
    assert pipeline[-2]["$project"]["day"] == "$_id"
    assert pipeline[-3]["$group"]["_id"] == {"$dateTrunc": {"date": "$date", "unit": "day"}}


def test_query_pipeline_count_includes_grouping_by_day_stage():
    pipeline = QueryByDay().count_pipeline()

    assert "$count" in pipeline[-1]
    assert pipeline[-2]["$project"]["day"] == "$_id"
    assert pipeline[-3]["$group"]["_id"] == {"$dateTrunc": {"date": "$date", "unit": "day"}}


@mock.patch(connection)
def test_read_report_by_day_empty_list(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.read_documents = paginate
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


@mock.patch(connection)
def test_read_report_by_day_list_fails_if_database_is_down(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.read_documents = paginate
    paginate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
