from unittest import mock

from pymongo.errors import ServerSelectionTimeoutError

from reports.filters import QueryByObject
from .. import utils


endpoint = "/by_object"


def test_query_pipeline_includes_grouping_stage():
    pipeline = QueryByObject().pipeline()
    group = {
            "_id": "$object",
            "first_date": {"$min": "$date"},
            "last_date": {"$max": "$date"},
            "users": {"$addToSet": "$owner"},
            "source": {"$addToSet": "$source"},
            "report_type": {"$addToSet": "$report_type"},
            "count": {"$count": {}},
        }

    pipeline = [stage for stage in pipeline if "$group" in stage or "$set" in stage]

    assert any("$group" in stage for stage in pipeline)
    assert any("$set" in stage for stage in pipeline)

    assert pipeline[0] == {"$group": group}
    assert pipeline[1] == {"$set": {"object": "$_id"}}


@mock.patch('reports.routes.database.get_connection')
def test_read_report_by_object_empty_list(mock_connection):
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


@mock.patch('reports.routes.database.get_connection')
def test_read_report_by_object_list_fails_if_database_is_down(mock_connection):
    paginate = mock.AsyncMock()
    mock_connection.return_value.read_paginated_documents = paginate
    paginate.side_effect = ServerSelectionTimeoutError()

    response = utils.client.get(endpoint)
    assert response.status_code == 503
