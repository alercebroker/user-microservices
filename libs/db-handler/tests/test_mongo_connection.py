from unittest import mock

import pytest
from db_handler import MongoConnection


input_settings = {
    "host": "host",
    "port": 1,
    "username": "user",
    "password": "pass",
    "database": "db"
}


def test_construction_has_proper_configuration():
    mock_settings = mock.MagicMock()
    mock_settings.dict.return_value = input_settings
    conn = MongoConnection(mock_settings)

    assert conn._config.db == input_settings["database"]
    expected_config = {k: v for k, v in input_settings.items() if k != "database"}
    assert conn._config == expected_config


def test_construction_turns_additional_options_to_lower_camel_case():
    extra = "non_pre_defined_key"
    extra_val = ""
    extra_output = "nonPreDefinedKey"
    new_input = input_settings.copy()
    new_input[extra] = extra_val

    mock_settings = mock.MagicMock()
    mock_settings.dict.return_value = new_input
    conn = MongoConnection(mock_settings)

    assert conn._config.db == new_input["database"]
    expected_config = {k: v for k, v in new_input.items() if k not in ("database", extra)}
    expected_config[extra_output] = extra_val
    assert conn._config == expected_config


def _check_missing(missing):
    bad_input = {k: v for k, v in input_settings.items() if k != missing}

    mock_settings = mock.MagicMock()
    mock_settings.dict.return_value = bad_input
    with pytest.raises(ValueError, match=f"Missing keys: {missing.upper()}"):
        MongoConnection(mock_settings)


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
