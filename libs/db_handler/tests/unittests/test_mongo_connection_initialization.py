from unittest import mock

import pytest
from db_handler import MongoConnection
from ..utils import input_settings


def test_construction_has_proper_configuration():
    conn = MongoConnection(**input_settings)

    assert conn._config.db == input_settings["database"]
    expected_config = {k: v for k, v in input_settings.items() if k != "database"}
    assert conn._config == expected_config


def test_construction_turns_additional_options_to_lower_camel_case():
    extra = "non_pre_defined_key"
    extra_val = ""
    extra_output = "nonPreDefinedKey"
    new_input = input_settings.copy()
    new_input[extra] = extra_val

    conn = MongoConnection(**new_input)

    assert conn._config.db == new_input["database"]
    expected_config = {k: v for k, v in new_input.items() if k not in ("database", extra)}
    expected_config[extra_output] = extra_val
    assert conn._config == expected_config


def _check_missing(missing):
    bad_input = {k: v for k, v in input_settings.items() if k != missing}
    with pytest.raises(ValueError, match=f"Missing keys: {missing.upper()}"):
        MongoConnection(**bad_input)


def test_construction_fails_if_missing_database():
    _check_missing("database")


def test_construction_fails_if_missing_host():
    _check_missing("host")


def test_construction_fails_if_missing_port():
    _check_missing("port")


def test_construction_fails_if_missing_username():
    _check_missing("username")


def test_construction_fails_if_missing_password():
    _check_missing("password")


@pytest.mark.asyncio
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_connection_creates_async_motor_client(mock_client):
    conn = MongoConnection(**input_settings)
    await conn.connect()

    assert conn._client == mock_client.return_value
    expected = {k: v for k, v in input_settings.items() if k != "database"}
    mock_client.assert_called_once_with(**expected, connect=True)


@pytest.mark.asyncio
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_connection_gets_db_from_client(mock_client):
    mock_db = mock.MagicMock()
    mock_client.return_value.__getitem__.return_value = mock_db

    conn = MongoConnection(**input_settings)
    await conn.connect()
    db = conn.db

    assert db == mock_db
    mock_client.return_value.__getitem__.assert_called_once_with(input_settings["database"])


@pytest.mark.asyncio
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_connection_closing(mock_client):
    conn = MongoConnection(**input_settings)
    await conn.connect()
    await conn.close()

    assert conn._client is None
    mock_client.return_value.close.assert_called_once()


@pytest.mark.asyncio
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_connection_using_async_context_manager(mock_client):
    async with MongoConnection(**input_settings) as conn:
        assert conn._client == mock_client.return_value
    assert conn._client is None
