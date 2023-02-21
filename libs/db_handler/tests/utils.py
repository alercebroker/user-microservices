from unittest import mock

from db_handler import MongoConnection


input_settings = {
    "host": "host",
    "port": 1,
    "username": "user",
    "password": "pass",
    "database": "db"
}


async def get_connection_and_db(mock_client):
    mock_db = mock.MagicMock()
    mock_client.return_value.__getitem__.return_value = mock_db

    conn = MongoConnection(**input_settings)
    await conn.connect()
    return conn, mock_db
