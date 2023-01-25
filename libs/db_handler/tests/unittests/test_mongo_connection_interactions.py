from unittest import mock

import pytest

from db_handler import PyObjectId, DocumentNotFound
from .. import utils


@pytest.mark.asyncio
@mock.patch('db_handler._connection.ModelMetaclass')
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_create_db_for_collection_with_indexes(mock_client, mock_model_meta):
    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.create_indexes = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"
    mock_model.__indexes__ = mock.MagicMock()
    mock_model_meta.__models__ = [mock_model]

    await conn.create_db()

    mock_db.__getitem__.assert_called_once_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.create_indexes.assert_called_once_with(mock_model.__indexes__)


@pytest.mark.asyncio
@mock.patch('db_handler._connection.ModelMetaclass')
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_create_db_for_collection_without_indexes(mock_client, mock_model_meta):
    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.create_indexes = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"
    mock_model.__indexes__ = []
    mock_model_meta.__models__ = [mock_model]

    await conn.create_db()

    mock_db.__getitem__.return_value.create_indexes.assert_not_called()


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_drop_db(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)
    conn._client.drop_database = mock.AsyncMock()

    await conn.drop_db()

    conn._client.drop_database.assert_called_once_with(mock_db)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_create_document_by_alias(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.insert_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_entry = {"field1": 1, "field2": 2}

    await conn.create_document(mock_model, mock_entry)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.insert_one.assert_awaited_once_with(mock_model.return_value.dict.return_value)
    mock_model.assert_called_once_with(**mock_entry)
    mock_model.return_value.dict.assert_called_once_with(by_alias=True)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_create_document_by_field(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.insert_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_entry = {"field1": 1, "field2": 2}

    await conn.create_document(mock_model, mock_entry, by_alias=False)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.insert_one.assert_awaited_once_with(mock_model.return_value.dict.return_value)
    mock_model.assert_called_once_with(**mock_entry)
    mock_model.return_value.dict.assert_called_once_with(by_alias=False)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_read_document_indexed_by_bson_object_id_casts_input_oid(mock_client):
    oid = "123456789012345678901234"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.find_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    await conn.read_document(mock_model, oid)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.find_one.assert_awaited_once_with({"_id": PyObjectId(oid)})


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_read_document_indexed_by_different_type_does_not_cast_input_oid(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.find_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    await conn.read_document(mock_model, oid)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.find_one.assert_awaited_once_with({"_id": oid})


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_read_document_fails_if_document_not_found(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.find_one = mock.AsyncMock()
    mock_db.__getitem__.return_value.find_one.return_value = None

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    with pytest.raises(DocumentNotFound, match=oid):
        await conn.read_document(mock_model, oid)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_update_document_indexed_by_bson_object_id_casts_input_oid(mock_client):
    oid = "123456789012345678901234"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_update = mock.AsyncMock()
    mock_db.__getitem__.return_value.find_one_and_update = mock_update

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_entry = {"field1": 1, "field2": 2}

    await conn.update_document(mock_model, oid, mock_entry)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    modify = {"$set": mock_entry}
    mock_update.assert_awaited_once_with({"_id": PyObjectId(oid)}, modify, return_document=True)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_update_document_indexed_by_different_type_does_not_cast_input_oid(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_update = mock.AsyncMock()
    mock_db.__getitem__.return_value.find_one_and_update = mock_update

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_entry = {"field1": 1, "field2": 2}

    await conn.update_document(mock_model, oid, mock_entry)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    modify = {"$set": mock_entry}
    mock_update.assert_awaited_once_with({"_id": oid}, modify, return_document=True)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_update_document_fails_if_document_not_found(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.find_one_and_update = mock.AsyncMock()
    mock_db.__getitem__.return_value.find_one_and_update.return_value = None

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_entry = {"field1": 1, "field2": 2}

    with pytest.raises(DocumentNotFound, match=oid):
        await conn.update_document(mock_model, oid, mock_entry)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_delete_document_indexed_by_bson_object_id_casts_input_oid(mock_client):
    oid = "123456789012345678901234"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.delete_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    await conn.delete_document(mock_model, oid)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.delete_one.assert_awaited_once_with({"_id": PyObjectId(oid)})


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_delete_document_indexed_by_different_type_does_not_cast_input_oid(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.delete_one = mock.AsyncMock()

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    await conn.delete_document(mock_model, oid)

    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.delete_one.assert_awaited_once_with({"_id": oid})


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_delete_document_fails_if_document_not_found(mock_client):
    oid = "plain_oid"

    conn, mock_db = await utils.get_connection_and_db(mock_client)
    mock_db.__getitem__.return_value.delete_one = mock.AsyncMock()
    mock_db.__getitem__.return_value.delete_one.return_value = mock.MagicMock()
    mock_db.__getitem__.return_value.delete_one.return_value.deleted_count = 0

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    with pytest.raises(DocumentNotFound, match=oid):
        await conn.delete_document(mock_model, oid)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_count_documents_with_empty_results(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)

    to_list = mock.AsyncMock()
    to_list.return_value = []
    mock_db.__getitem__.return_value.aggregate.return_value.to_list = to_list

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_query = mock.MagicMock()

    n = await conn.count_documents(mock_model, mock_query)

    assert n == 0
    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.aggregate.assert_called_once_with(mock_query.count_pipeline.return_value)
    to_list.assert_awaited_once_with(1)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_count_documents_with_results(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)

    to_list = mock.AsyncMock()
    to_list.return_value = [{"total": 2}]
    mock_db.__getitem__.return_value.aggregate.return_value.to_list = to_list

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_query = mock.MagicMock()

    n = await conn.count_documents(mock_model, mock_query)

    assert n == 2
    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.aggregate.assert_called_once_with(mock_query.count_pipeline.return_value)
    to_list.assert_awaited_once_with(1)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_read_document_list(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)

    async_for = mock.AsyncMock()
    async_for.__aiter__.return_value = [{}, {}, {}]
    mock_db.__getitem__.return_value.aggregate.return_value = async_for

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_query = mock.MagicMock()

    docs = await conn.read_documents(mock_model, mock_query)

    assert docs == async_for.__aiter__.return_value
    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.aggregate.assert_called_once_with(mock_query.pipeline.return_value)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_pagination_for_empty_results(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)

    to_list = mock.AsyncMock()
    mock_db.__getitem__.return_value.aggregate.return_value.to_list = to_list

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_query = mock.MagicMock()
    mock_query.page = 1
    mock_query.limit = 10
    mock_query.skip = 0

    conn.count_documents = mock.AsyncMock()
    conn.count_documents.return_value = 0

    paginated = await conn.paginate_documents(mock_model, mock_query)

    assert paginated == to_list.return_value
    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.aggregate.assert_called_once_with(mock_query.pipeline.return_value)
    to_list.assert_called_once_with(mock_query.limit)


@pytest.mark.asyncio
@mock.patch('db_handler._connection._MongoConfig', new=mock.MagicMock())
@mock.patch('db_handler._connection.AsyncIOMotorClient')
async def test_pagination_with_results(mock_client):
    conn, mock_db = await utils.get_connection_and_db(mock_client)

    to_list = mock.AsyncMock()
    mock_db.__getitem__.return_value.aggregate.return_value.to_list = to_list

    mock_model = mock.MagicMock()
    mock_model.__tablename__ = "tablename"

    mock_query = mock.MagicMock()
    mock_query.page = 1
    mock_query.limit = 10
    mock_query.skip = (mock_query.page - 1) * mock_query.limit

    conn.count_documents = mock.AsyncMock()
    conn.count_documents.return_value = 30

    paginated = await conn.paginate_documents(mock_model, mock_query)

    assert paginated == to_list.return_value
    mock_db.__getitem__.assert_called_with(mock_model.__tablename__)
    mock_db.__getitem__.return_value.aggregate.assert_called_once_with(mock_query.pipeline.return_value)
    to_list.assert_called_once_with(mock_query.limit)
