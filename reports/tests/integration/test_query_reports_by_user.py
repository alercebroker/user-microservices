import pytest

from .. import utils

endpoint = '/count_by_user'

total_reports = 10
total = 4  # Number of users in mongo-init.js

cutoff_date = '2023-01-01T12:00:01'
total_before = 4


@pytest.mark.usefixtures('mongo_service')
def test_query_order_by_user_ascending():
    with utils.client:
        result = utils.client.get(endpoint, params={'order_by': 'user', 'direction': 1})

    assert result.status_code == 200
    assert len(result.json()) == total

    dates = [report["user"] for report in result.json()]
    assert dates == sorted(dates)


@pytest.mark.usefixtures('mongo_service')
def test_query_order_by_user_descending():
    with utils.client:
        result = utils.client.get(endpoint, params={'order_by': 'user', 'direction': -1})

    assert result.status_code == 200

    dates = [obj["user"] for obj in result.json()]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.usefixtures('mongo_service')
def test_query_by_object_full_name():
    obj = 'OBJECT1'
    expected = 3  # must match with mongo-init.js
    with utils.client:
        result = utils.client.get(endpoint, params={'object': obj})

    assert result.status_code == 200
    assert 0 < len(result.json()) < total  # Just to make sure there's something here

    assert sum(report["count"] for report in result.json()) == expected


@pytest.mark.usefixtures('mongo_service')
def test_query_by_object_regex():
    obj = 'OBJECT(1|2)'
    expected = 6  # must match with mongo-init.js
    with utils.client:
        result = utils.client.get(endpoint, params={'object': obj})

    assert result.status_code == 200
    assert 0 < len(result.json()) < total  # Just to make sure there's something here

    assert sum(report["count"] for report in result.json()) == expected


@pytest.mark.usefixtures('mongo_service')
def test_query_by_date_before():
    with utils.client:
        result = utils.client.get(endpoint, params={'date_before': cutoff_date})

    assert result.status_code == 200

    assert sum(report["count"] for report in result.json()) == total_before


@pytest.mark.usefixtures('mongo_service')
def test_query_by_date_after():
    with utils.client:
        result = utils.client.get(endpoint, params={'date_after': cutoff_date})

    assert result.status_code == 200

    assert sum(report["count"] for report in result.json()) == total_reports - total_before
