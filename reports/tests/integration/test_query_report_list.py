import pytest

from .. import utils

endpoint = '/'

total = 10  # Number of reports in mongo-init.js
page_size = total // 3
last_page = 3 + (1 if total % 3 else 0)

cutoff_date = '2023-01-01T23:59:59'


@pytest.mark.usefixtures('mongo_service')
def test_query_order_by_date_ascending():
    with utils.client:
        result = utils.client.get(endpoint, params={'order_by': 'date', 'direction': 1})

    assert result.status_code == 200
    assert result.json()["count"] == len(result.json()["results"]) == total

    dates = [report["date"] for report in result.json()["results"]]
    assert dates == sorted(dates)


@pytest.mark.usefixtures('mongo_service')
def test_query_order_by_date_descending():
    with utils.client:
        result = utils.client.get(endpoint, params={'order_by': 'date', 'direction': -1})

    assert result.status_code == 200

    dates = [obj["date"] for obj in result.json()["results"]]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.usefixtures('mongo_service')
def test_query_pagination_single_page():
    with utils.client:
        result = utils.client.get(endpoint, params={'page_size': total})

    assert result.status_code == 200
    assert result.json()["count"] == total

    assert result.json()["previous"] is None
    assert result.json()["next"] is None
    assert len(result.json()["results"]) == total


@pytest.mark.usefixtures('mongo_service')
def test_query_pagination_first_page():
    with utils.client:
        result = utils.client.get(endpoint, params={'page_size': page_size, 'page': 1})

    assert result.status_code == 200
    assert result.json()["count"] == total

    assert result.json()["previous"] is None
    assert result.json()["next"] == 2
    assert len(result.json()["results"]) == page_size


@pytest.mark.usefixtures('mongo_service')
def test_query_pagination_middle_page():
    with utils.client:
        result = utils.client.get(endpoint, params={'page_size': page_size, 'page': 2})

    assert result.status_code == 200
    assert result.json()["count"] == total

    assert result.json()["previous"] == 1
    assert result.json()["next"] == 3
    assert len(result.json()["results"]) == page_size


@pytest.mark.usefixtures('mongo_service')
def test_query_pagination_last_page():
    with utils.client:
        result = utils.client.get(endpoint, params={'page_size': page_size, 'page': last_page})

    assert result.status_code == 200
    assert result.json()["count"] == total

    assert result.json()["previous"] == last_page - 1
    assert result.json()["next"] is None
    assert len(result.json()["results"]) == (page_size if last_page == 3 else total % 3)


@pytest.mark.usefixtures('mongo_service')
def test_query_by_object_full_name():
    obj = 'OBJECT1'
    with utils.client:
        result = utils.client.get(endpoint, params={'object': obj})

    assert result.status_code == 200
    assert 0 < result.json()["count"] < total  # Just to make sure there's something here

    assert all(report["object"] == obj for report in result.json()["results"])


@pytest.mark.usefixtures('mongo_service')
def test_query_by_object_regex():
    obj = 'OBJECT(1|2)'
    expected = ['OBJECT1', 'OBJECT2']
    with utils.client:
        result = utils.client.get(endpoint, params={'object': obj})

    assert result.status_code == 200
    assert 0 < result.json()["count"] < total  # Just to make sure there's something here

    assert all(report["object"] in expected for report in result.json()["results"])


@pytest.mark.usefixtures('mongo_service')
def test_query_by_date_before():
    with utils.client:
        result = utils.client.get(endpoint, params={'date_before': cutoff_date})

    assert result.status_code == 200
    assert 0 < result.json()["count"] < total  # Just to make sure there's something here

    assert all(report["date"] <= cutoff_date for report in result.json()["results"])


@pytest.mark.usefixtures('mongo_service')
def test_query_by_date_after():
    with utils.client:
        result = utils.client.get(endpoint, params={'date_after': cutoff_date})

    assert result.status_code == 200
    assert 0 < result.json()["count"] < total  # Just to make sure there's something here

    assert all(report["date"] >= cutoff_date for report in result.json()["results"])
