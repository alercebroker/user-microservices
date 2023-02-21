from unittest import mock

from reports.database import get_connection

from .. import utils


@mock.patch('reports.main.database')
def test_startup_and_shutdown(mock_database):
    mock_connection = mock_database.get_connection
    mock_connection.return_value.connect = mock.AsyncMock()
    mock_connection.return_value.create_db = mock.AsyncMock()
    mock_connection.return_value.close = mock.AsyncMock()
    mock_connection.return_value.drop_db = mock.AsyncMock()

    with utils.client:
        pass

    mock_connection.return_value.connect.assert_awaited_once()
    mock_connection.return_value.create_db.assert_awaited_once()
    mock_connection.return_value.close.assert_awaited_once()
    mock_connection.return_value.drop_db.assert_not_called()


def test_mongo_connection_initialization():
    db = get_connection()
    assert db._config.db == "test"
    assert db._config["host"] == "localhost"
    assert db._config["port"] == 27017
    assert db._config["username"] == "user"
    assert db._config["password"] == "password"
    assert db._alerts_url == "mock_url"
