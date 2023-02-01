import pytest
import pytest_asyncio
from pydantic import BaseModel, Field, dataclasses
from pydantic.error_wrappers import ValidationError
from pymongo import IndexModel
from query import BaseQuery, BasePaginatedQuery, QueryRecipe

from db_handler import DocumentNotFound, MongoConnection, ModelMetaclass, PyObjectId


settings = {
    "host": "localhost",
    "port": 27017,
    "username": "user",
    "password": "password",
    "database": "test"
}


class MockDocument(BaseModel, metaclass=ModelMetaclass):
    __tablename__ = "table"
    __indexes__ = [IndexModel([("field2", 1)])]

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    field1: int


@dataclasses.dataclass
class Queries:
    min_field: int

    recipes = (QueryRecipe("field1", ["$gte"], ["min_field"]),)


@dataclasses.dataclass
class MockQuery(Queries, BaseQuery):
    pass


@dataclasses.dataclass
class MockPaginatedQuery(BasePaginatedQuery, Queries):
    order_by: str = "field1"


oid = "123456789012345678901234"
insert = dict(_id=PyObjectId(oid), field1=1)


@pytest_asyncio.fixture
async def connection():
    conn = MongoConnection(**settings)
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
    document = await connection.create_document(MockDocument, insert)

    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected == document == insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_create_document_with_missing_field_fails(connection):
    with pytest.raises(ValidationError, match="field required"):
        await connection.create_document(MockDocument, {k: v for k, v in insert.items() if k != "field1"})


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_document(connection):
    db = connection.db
    await db["table"].insert_one(insert)

    document = await connection.read_document(MockDocument, oid)

    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected == document == insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_non_existent_document_fails(connection):
    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected is None

    with pytest.raises(DocumentNotFound):
        await connection.read_document(MockDocument, oid)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_update_document(connection):
    db = connection.db
    await db["table"].insert_one(insert)

    document = await connection.update_document(MockDocument, oid, {"field2": -1})

    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected == document != insert


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_update_non_existent_document_fails(connection):
    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected is None

    with pytest.raises(DocumentNotFound):
        await connection.update_document(MockDocument, oid, {"field2": -1})


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_delete_document(connection):
    db = connection.db
    await db["table"].insert_one(insert)

    await connection.delete_document(MockDocument, oid)

    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_delete_non_existent_document_fails(connection):
    db = connection.db
    expected = await db["table"].find_one({"_id": PyObjectId(oid)})
    assert expected is None

    with pytest.raises(DocumentNotFound):
        await connection.delete_document(MockDocument, oid)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_count_documents_with_elements(connection):
    db = connection.db
    await db["table"].insert_many([{"field1": _} for _ in range(30)])

    q = MockQuery(min_field=15)
    actual = await connection.count_documents(MockDocument, q)

    assert actual == 15


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_count_documents_without_elements(connection):
    db = connection.db
    await db["table"].insert_many([{"field1": _} for _ in range(30)])

    q = MockQuery(min_field=31)
    actual = await connection.count_documents(MockDocument, q)

    assert actual == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_document_list_with_elements(connection):
    db = connection.db
    await db["table"].insert_many([{"field1": _} for _ in range(30)])

    q = MockQuery(min_field=15)
    actual = await connection.read_documents(MockDocument, q)

    assert actual == [_ async for _ in db["table"].find({"field1": {"$gte": 15}})]


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_document_list_without_elements(connection):
    db = connection.db
    await db["table"].insert_many([{"field1": _} for _ in range(30)])

    q = MockQuery(min_field=31)
    actual = await connection.read_documents(MockDocument, q)

    assert actual == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("mongo_service")
async def test_read_paginated_documents_with_elements(connection):
    db = connection.db
    await db["table"].insert_many([{"field1": _} for _ in range(30)])

    q = MockPaginatedQuery(min_field=15, page_size=5, page=2, direction=1)
    actual = await connection.read_documents(MockDocument, q)

    assert actual == [_ async for _ in db["table"].find({"field1": {"$gte": 15}}).skip(5).limit(5)]
