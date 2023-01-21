import os
from unittest import mock

from reports.database import get_settings, get_connection

from .. import utils


@mock.patch('reports.main.get_connection')
def test_startup_and_shutdown(mock_connection):
    mock_connection.return_value.connect = mock.AsyncMock()
    mock_connection.return_value.create_db = mock.AsyncMock()
    mock_connection.return_value.close = mock.AsyncMock()
    mock_connection.return_value.drop_db = mock.AsyncMock()

    with utils.client:
        pass

    mock_connection.return_value.connect.assert_awaited_once()
    mock_connection.return_value.create_db.assert_awaited_once()
    mock_connection.return_value.close.assert_awaited_once()
    mock_connection.return_value.drop_db.assert_not_awaited()


def test_mongo_settings_initializes():
    settings = get_settings()
    assert settings.host == "localhost"
    assert settings.port == 27017
    assert settings.username == "user"
    assert settings.password == "password"
    assert settings.database == "test"


def test_mongo_connection_initialization():
    connection = get_connection()
    assert connection._config.db == "test"
    assert connection._config["host"] == "localhost"
    assert connection._config["port"] == 27017
    assert connection._config["username"] == "user"
    assert connection._config["password"] == "password"
