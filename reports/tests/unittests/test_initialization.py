from unittest import mock

from reports.database import db

from .. import utils


@mock.patch('reports.main.db')
def test_startup_and_shutdown(mock_connection):
    mock_connection.connect = mock.AsyncMock()
    mock_connection.create_db = mock.AsyncMock()
    mock_connection.close = mock.AsyncMock()
    mock_connection.drop_db = mock.AsyncMock()

    with utils.client:
        pass

    mock_connection.connect.assert_awaited_once()
    mock_connection.create_db.assert_awaited_once()
    mock_connection.close.assert_awaited_once()
    mock_connection.drop_db.assert_not_awaited()


def test_mongo_connection_initialization():
    assert db._config.db == "test"
    assert db._config["host"] == "localhost"
    assert db._config["port"] == 27017
    assert db._config["username"] == "user"
    assert db._config["password"] == "password"
    assert db._alerts_url == "mock_url"
