from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from reports.filters import QueryByObject
from .. import utils


endpoint = "/by_object"

connection = 'reports.routes.db'


def test_query_pipeline_includes_grouping_by_object_stage():
    pipeline = QueryByObject().pipeline()

    assert "$limit" in pipeline[-1]
    assert "$skip" in pipeline[-2]
    assert "$sort" in pipeline[-3]
    assert pipeline[-4]["$project"]["object"] == "$_id"
    assert pipeline[-5]["$group"]["_id"] == "$object"


def test_query_pipeline_count_includes_grouping_by_object_stage():
    pipeline = QueryByObject().count_pipeline()

    assert "$count" in pipeline[-1]
    assert pipeline[-2]["$project"]["object"] == "$_id"
    assert pipeline[-3]["$group"]["_id"] == "$object"


@mock.patch(connection)
def test_read_report_by_object_empty_list(mock_connection):
    count, paginate = mock.AsyncMock(), mock.AsyncMock()
    mock_connection.count_documents = count
    mock_connection.paginate_documents = paginate
    count.return_value = 0
    paginate.return_value = []

    response = utils.client.get(endpoint)
    assert response.status_code == 200
    assert response.json() == {"count": 0, "next": None, "previous": None, "results": paginate.return_value}


def test_read_report_by_object_list_fails_if_order_by_is_unknown():
    response = utils.client.get(endpoint, params={"order_by": "unknown"})
    assert response.status_code == 422


def test_read_report_by_object_list_fails_if_direction_is_unknown():
    response = utils.client.get(endpoint, params={"direction": 0})
    assert response.status_code == 422


def test_read_report_by_object_list_fails_if_page_is_less_than_one():
    response = utils.client.get(endpoint, params={"page": 0})
    assert response.status_code == 422


def test_read_report_by_object_list_fails_if_page_size_is_less_than_one():
    response = utils.client.get(endpoint, params={"page_size": 0})
    assert response.status_code == 422


@mock.patch(connection)
def test_read_report_by_object_list_fails_if_database_is_down(mock_connection):
    count = mock.AsyncMock()
    mock_connection.count_documents = count
    count.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
