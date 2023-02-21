import io
from datetime import datetime
from unittest import mock

import pandas as pd
import pytest
from astropy.time import Time
from pandas.testing import assert_frame_equal
from pymongo.errors import ServerSelectionTimeoutError

from reports.database import get_connection
from .. import utils

endpoint = "/csv_reports"

client = 'reports.database._connection.httpx'
connection = 'reports.routes.db'


@pytest.fixture(scope="module")
def define_constants():
    httpx_client_output = {
        "items": [
            dict(oid="OID1", ndet=1, firstmjd=50000, lastmjd=50000, other1="mock1", other2="mock2"),
            dict(oid="OID2", ndet=2, firstmjd=50000, lastmjd=60000, other1="mock3", other2="mock4"),
        ]
    }

    query_objects_output = pd.DataFrame([
        dict(
            object=httpx_client_output["items"][0]["oid"],
            nobs=httpx_client_output["items"][0]["ndet"],
            first_detection=httpx_client_output["items"][0]["firstmjd"],
            last_detection=httpx_client_output["items"][0]["lastmjd"]
        ),
        dict(
            object=httpx_client_output["items"][1]["oid"],
            nobs=httpx_client_output["items"][1]["ndet"],
            first_detection=httpx_client_output["items"][1]["firstmjd"],
            last_detection=httpx_client_output["items"][1]["lastmjd"]
        ),
    ]).set_index("object")

    documents_output = [
        dict(
            object=httpx_client_output["items"][0]["oid"],
            first_date=datetime(2020, 1, 1, 12, 0, 0),
            last_date=datetime(2020, 1, 2, 12, 0, 0),
            count=2,
            report_type="TOM",
            users=["user1", "user2"]
        ),
        dict(
            object=httpx_client_output["items"][1]["oid"],
            first_date=datetime(2021, 1, 1, 12, 0, 0),
            last_date=datetime(2021, 1, 2, 12, 0, 0),
            count=1,
            report_type="TOM",
            users=["user1"]
        )
    ]
    expected_output = pd.DataFrame([
        dict(
            object=documents_output[0]["object"],
            first_date=documents_output[0]["first_date"].isoformat(timespec="milliseconds"),
            last_date=documents_output[0]["last_date"].isoformat(timespec="milliseconds"),
            count=documents_output[0]["count"],
            report_type=documents_output[0]["report_type"],
            nobs=httpx_client_output["items"][0]["ndet"],
            first_detection=Time(httpx_client_output["items"][0]["firstmjd"], format="mjd").to_value("isot"),
            last_detection=Time(httpx_client_output["items"][0]["lastmjd"], format="mjd").to_value("isot")
        ),
        dict(
            object=documents_output[1]["object"],
            first_date=documents_output[1]["first_date"].isoformat(timespec="milliseconds"),
            last_date=documents_output[1]["last_date"].isoformat(timespec="milliseconds"),
            count=documents_output[1]["count"],
            report_type=documents_output[1]["report_type"],
            nobs=httpx_client_output["items"][1]["ndet"],
            first_detection=Time(httpx_client_output["items"][1]["firstmjd"], format="mjd").to_value("isot"),
            last_detection=Time(httpx_client_output["items"][1]["lastmjd"], format="mjd").to_value("isot")
        ),
    ]).set_index("object")
    return httpx_client_output, query_objects_output, documents_output, expected_output


@mock.patch(client)
def test_db_connection_query_objects_selects_and_renames_columns(mock_httpx, define_constants):
    httpx_client_output, query_objects_output, _, _ = define_constants
    objects = httpx_client_output.copy()
    mock_httpx.Client.return_value.__enter__.return_value.get.return_value.is_error = False
    mock_httpx.Client.return_value.__enter__.return_value.get.return_value.json.return_value = objects

    db = get_connection()
    output = db.query_objects([])
    assert_frame_equal(output, query_objects_output)


@mock.patch(client)
def test_db_connection_query_objects_removes_duplicates(mock_httpx, define_constants):
    httpx_client_output, query_objects_output, _, _ = define_constants
    objects = httpx_client_output.copy()
    objects["items"] = objects["items"] + objects["items"]
    mock_httpx.Client.return_value.__enter__.return_value.get.return_value.is_error = False
    mock_httpx.Client.return_value.__enter__.return_value.get.return_value.json.return_value = objects

    db = get_connection()
    output = db.query_objects([])
    assert_frame_equal(output, query_objects_output)


@mock.patch(client)
def test_db_connection_raises_connection_error_if_request_fails(mock_httpx):
    mock_httpx.Client.return_value.__enter__.return_value.get.return_value.is_error = True

    db = get_connection()
    with pytest.raises(ConnectionError, match="Cannot connect"):
        db.query_objects([])


@mock.patch(connection)
def test_download_csv_reports_joins_values_by_object_id(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy()

    response = utils.client.get("/csv_reports", params={"order_by": "object", "direction": 1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    assert_frame_equal(output, expected_output)


@mock.patch(connection)
def test_download_csv_reports_keeps_order_of_documents_by_object(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy().loc[["OID2", "OID1"]]

    response = utils.client.get("/csv_reports", params={"order_by": "object", "direction": -1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    assert_frame_equal(output, expected_output.sort_index(ascending=False))


@mock.patch(connection)
def test_download_csv_reports_keeps_order_of_documents_by_other_key(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy()

    response = utils.client.get("/csv_reports", params={"order_by": "count", "direction": 1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    assert_frame_equal(output, expected_output.sort_values(by="count"))


@mock.patch(connection)
def test_download_csv_reports_excludes_objects_with_no_match_in_documents(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output[:-1]
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy()

    response = utils.client.get("/csv_reports", params={"order_by": "object", "direction": 1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    assert_frame_equal(output, expected_output.loc[["OID1"]])


@mock.patch(connection)
def test_download_csv_reports_keeps_documents_with_no_match_in_objects(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy().loc[["OID1"]]

    response = utils.client.get("/csv_reports", params={"order_by": "object", "direction": 1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    expected_output = expected_output.copy()
    expected_output.loc["OID2", ["nobs", "first_detection", "last_detection"]] = float("nan")
    assert_frame_equal(output, expected_output)


@mock.patch(connection)
def test_download_csv_reports_keeps_duplicate_documents(mock_connection, define_constants):
    _, query_objects_output, documents_output, expected_output = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output + documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.return_value = query_objects_output.copy()

    response = utils.client.get("/csv_reports", params={"order_by": "object", "direction": 1})
    output = pd.read_csv(io.BytesIO(response.content), index_col="object")

    expected_output = pd.concat([expected_output, expected_output])
    assert_frame_equal(output, expected_output.sort_index())


@mock.patch(connection)
def test_download_csv_fails_if_database_is_down(mock_connection):
    read_documents = mock.AsyncMock()
    read_documents.side_effect = ServerSelectionTimeoutError()
    mock_connection.read_documents = read_documents

    response = utils.client.get("/csv_reports")
    assert response.status_code == 503


@mock.patch(connection)
def test_download_csv_fails_if_alerts_api_is_down(mock_connection, define_constants):
    _, _, documents_output, _ = define_constants
    read_documents = mock.AsyncMock()
    read_documents.return_value = documents_output
    mock_connection.read_documents = read_documents
    mock_connection.query_objects.side_effect = ConnectionError("")

    response = utils.client.get("/csv_reports")
    assert response.status_code == 503
