from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from reports.filters import QueryByDay
from .. import utils


endpoint = "/count_by_day"


def test_query_pipeline_includes_grouping_stage():
    pipeline = QueryByDay().pipeline()
    group = {"_id": {"$dateTrunc": {"date": "$date", "unit": "day"}}, "count": {"$count": {}}}

    pipeline = [stage for stage in pipeline if "$group" in stage or "$set" in stage]

    assert any("$group" in stage for stage in pipeline)
    assert any("$set" in stage for stage in pipeline)

    assert pipeline[0] == {"$group": group}
    assert pipeline[1] == {"$set": {"day": "$_id"}}


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
