import pytest
import pytest_asyncio
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError
from pymongo import IndexModel

from db_handler import MongoConnection, ModelMetaclass, PyObjectId, DocumentNotFound


settings = {
    "host": "localhost",
    "port": 27017,
    "username": "user",
    "password": "password",
    "database": "test"
}


class Document(BaseModel, metaclass=ModelMetaclass):
    __tablename__ = "table"
    __indexes__ = [IndexModel([("field2", 1)])]

    id: PyObjectId = Field(..., alias="_id")
    field1: str
    field2: int


oid = "123456789012345678901234"
insert = dict(_id=PyObjectId(oid), field1="mock", field2=1)


@pytest_asyncio.fixture
async def connection():
    conn = MongoConnection(settings)
    await conn.connect()
    await conn.create_db()
    yield conn
    await conn.drop_db()
    await conn.close()


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_database_corresponds_to_settings(connection):
    db = connection.db
    assert db.name == "test"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_collection_is_created_with_indexes(connection):
    db = connection.db
    collections = await db.list_collection_names()
    assert collections == ["table"]

    indexes = await db["table"].index_information()
    assert "field2_1" in indexes


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_create_document(connection):
    document = await connection.create_document(Document, insert)

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual == document == insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_create_document_with_missing_field_fails(connection):
    with pytest.raises(ValidationError, match="field required"):
        await connection.create_document(Document, {k: v for k, v in insert.items() if k != "field1"})


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_document(connection):
    await connection.create_document(Document, insert)

    document = await connection.read_document(Document, oid)

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual == document == insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_non_existent_document_fails(connection):
    with pytest.raises(DocumentNotFound, match=oid):
        await connection.read_document(Document, oid)

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_update_document(connection):
    await connection.create_document(Document, insert)

    document = await connection.update_document(Document, oid, {"field2": -1})

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual == document != insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_update_non_existent_document_fails(connection):
    with pytest.raises(DocumentNotFound, match=oid):
        await connection.update_document(Document, oid, {"field2": -1})

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_delete_document(connection):
    await connection.create_document(Document, insert)

    await connection.delete_document(Document, oid)

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_delete_non_existent_document_fails(connection):
    with pytest.raises(DocumentNotFound, match=oid):
        await connection.delete_document(Document, oid)

    db = connection.db
    actual = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert actual is None
