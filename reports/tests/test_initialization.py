import os
from unittest import mock

from reports.database import get_settings, get_connection

from . import utils


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


def test_mongo_settings_initializes_with_env_variables():
    os.environ["MONGODB_HOST"] = "host"
    os.environ["MONGODB_PORT"] = "27017"
    os.environ["MONGODB_USERNAME"] = "user"
    os.environ["MONGODB_PASSWORD"] = "pass"
    os.environ["MONGODB_DATABASE"] = "db"

    settings = get_settings()
    assert settings.host == "host"
    assert settings.port == 27017
    assert settings.username == "user"
    assert settings.password == "pass"
    assert settings.database == "db"


def test_mongo_connection_initialization():
    os.environ["MONGODB_HOST"] = "host"
    os.environ["MONGODB_PORT"] = "27017"
    os.environ["MONGODB_USERNAME"] = "user"
    os.environ["MONGODB_PASSWORD"] = "pass"
    os.environ["MONGODB_DATABASE"] = "db"

    connection = get_connection()
    assert connection._config.db == "db"
    assert connection._config["host"] == "host"
    assert connection._config["port"] == 27017
    assert connection._config["username"] == "user"
    assert connection._config["password"] == "pass"
