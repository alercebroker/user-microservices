import json

import pytest

from .. import utils

report_input = {
    "object": "OBJECT0",
    "solved": False,
    "source": "source0",
    "observation": "obs0",
    "report_type": "type0",
    "owner": "user0"
}
different_input = {
    "object": "NEWOBJECT",
    "solved": True,
    "source": "new_source",
    "observation": "new_obs",
    "report_type": "new_type",
    "owner": "new_user"
}


@pytest.mark.usefixtures('mongo_service')
def test_delete_report():
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        check = utils.client.delete(f'/{insert.json()["_id"]}')

    assert check.status_code == 204


@pytest.mark.usefixtures('mongo_service')
def test_post_report():
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        check = utils.client.get(f'/{insert.json()["_id"]}')
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert check.status_code == 200

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == report_input


@pytest.mark.usefixtures('mongo_service')
def test_post_report_with_missing_field_fails():
    bad_input = {k: v for k, v in report_input.items() if k != "object"}
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(bad_input))

    assert insert.status_code == 422


@pytest.mark.usefixtures('mongo_service')
def test_post_report_duplicate_fails():
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        insert_duplicate = utils.client.post('/', content=json.dumps(report_input))
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert insert_duplicate.status_code == 400


@pytest.mark.usefixtures('mongo_service')
def test_put_report():
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        put = utils.client.put(f'/{insert.json()["_id"]}', content=json.dumps(different_input))
        check = utils.client.get(f'/{insert.json()["_id"]}')
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert put.status_code == 200
    assert check.status_code == 200

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == different_input
    assert check.json()["_id"] == insert.json()["_id"]
    assert check.json()["date"] == insert.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_put_report_with_missing_field_fails():
    bad_input = {k: v for k, v in different_input.items() if k != "object"}
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        put = utils.client.put(f'/{insert.json()["_id"]}', content=json.dumps(bad_input))
        check = utils.client.get(f'/{insert.json()["_id"]}')
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert put.status_code == 422
    assert check.status_code == 200

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == report_input
    assert check.json()["_id"] == insert.json()["_id"]
    assert check.json()["date"] == insert.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_put_report_duplicate_fails():
    with utils.client:
        insert1 = utils.client.post('/', content=json.dumps(report_input))
        insert2 = utils.client.post('/', content=json.dumps(different_input))
        put = utils.client.put(f'/{insert1.json()["_id"]}', content=json.dumps(different_input))
        check = utils.client.get(f'/{insert1.json()["_id"]}')
        utils.client.delete(f'/{insert1.json()["_id"]}')
        utils.client.delete(f'/{insert2.json()["_id"]}')

    assert insert1.status_code == 201
    assert insert2.status_code == 201
    assert put.status_code == 400

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == report_input
    assert check.json()["_id"] == insert1.json()["_id"]
    assert check.json()["date"] == insert1.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_patch_report():
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        patch = utils.client.patch(f'/{insert.json()["_id"]}', content=json.dumps(different_input))
        check = utils.client.get(f'/{insert.json()["_id"]}')
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert patch.status_code == 200
    assert check.status_code == 200

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == different_input
    assert check.json()["_id"] == insert.json()["_id"]
    assert check.json()["date"] == insert.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_patch_report_with_missing_field_leaves_field_unmodified():
    incomplete_input = {k: v for k, v in different_input.items() if k != "object"}
    with utils.client:
        insert = utils.client.post('/', content=json.dumps(report_input))
        patch = utils.client.patch(f'/{insert.json()["_id"]}', content=json.dumps(incomplete_input))
        check = utils.client.get(f'/{insert.json()["_id"]}')
        utils.client.delete(f'/{insert.json()["_id"]}')

    assert insert.status_code == 201
    assert patch.status_code == 200
    assert check.status_code == 200

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    expected = incomplete_input.copy()
    expected["object"] = report_input["object"]
    assert actual == expected
    assert check.json()["_id"] == insert.json()["_id"]
    assert check.json()["date"] == insert.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_patch_report_duplicate_fails():
    with utils.client:
        insert1 = utils.client.post('/', content=json.dumps(report_input))
        insert2 = utils.client.post('/', content=json.dumps(different_input))
        patch = utils.client.patch(f'/{insert1.json()["_id"]}', content=json.dumps(different_input))
        check = utils.client.get(f'/{insert1.json()["_id"]}')
        utils.client.delete(f'/{insert1.json()["_id"]}')
        utils.client.delete(f'/{insert2.json()["_id"]}')

    assert insert1.status_code == 201
    assert insert2.status_code == 201
    assert patch.status_code == 400

    actual = {k: v for k, v in check.json().items() if k not in {"_id", "date"}}
    assert actual == report_input
    assert check.json()["_id"] == insert1.json()["_id"]
    assert check.json()["date"] == insert1.json()["date"]


@pytest.mark.usefixtures('mongo_service')
def test_get_non_existing_report_fails():
    with utils.client:
        # Impossible OID
        check = utils.client.get(f'/oid')

    assert check.status_code == 404


@pytest.mark.usefixtures('mongo_service')
def test_put_non_existing_report_fails():
    with utils.client:
        # Impossible OID
        check = utils.client.put(f'/oid', content=json.dumps(report_input))

    assert check.status_code == 404


@pytest.mark.usefixtures('mongo_service')
def test_patch_non_existing_report_fails():
    with utils.client:
        # Impossible OID
        check = utils.client.patch(f'/oid', content=json.dumps(report_input))

    assert check.status_code == 404


@pytest.mark.usefixtures('mongo_service')
def test_delete_non_existing_report_fails():
    with utils.client:
        # Impossible OID
        check = utils.client.delete(f'/oid')

    assert check.status_code == 404
