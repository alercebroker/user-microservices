from collections import UserDict
from typing import Any

from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, BaseSettings
from query import BaseQuery, BasePaginatedQuery

from ._utils import DocumentNotFound, ModelMetaclass, PyObjectId


class _MongoConfig(UserDict):
    """Special dictionary used to parse configuration dictionaries for mongodb.

    The required keys are described in `REQUIRED_KEYS`, but can come with any
    capitalization.

    All keys are converted from `snake_case` to `lowerCamelCase` format, as
    used by `motor` (python asynchronous driver for MongoDB). The special key
    `database` is removed from the dictionary proper, but can be accessed
    through the property `db`.
    """

    REQUIRED_KEYS = {"host", "username", "password", "port", "database"}

    def __init__(self, seq=None, **kwargs):
        super().__init__(seq, **kwargs)
        if self.REQUIRED_KEYS.difference(self.keys()):
            missing = ", ".join(key.upper() for key in self.REQUIRED_KEYS.difference(self.keys()))
            raise ValueError(f"Invalid configuration. Missing keys: {missing}")
        self._db = self.pop("database")

    @property
    def db(self) -> str:
        """str: database name"""
        return self._db

    def __setitem__(self, key: str, value: Any):
        """Converts keys from (case-insensitive) `snake_case` to `lowerCamelCase`"""
        klist = [w.lower() if i == 0 else w.title() for i, w in enumerate(key.split("_"))]
        super().__setitem__("".join(klist), value)


class MongoConnection:
    def __init__(self, config: BaseSettings):
        self._config = _MongoConfig(config.dict())
        self._client = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self._client[self._config.db]

    async def connect(self):
        self._client = AsyncIOMotorClient(connect=True, **self._config)

    async def close(self):
        self._client.close()
        self._client = None

    async def create_db(self):
        for cls in ModelMetaclass.__models__:
            if cls.__indexes__:
                await self.db[cls.__tablename__].create_indexes(cls.__indexes__)

    async def drop_db(self):
        await self._client.drop_database(self.db)

    async def create_document(self, model: ModelMetaclass, document: dict, by_alias: bool = True) -> dict:
        document = model(**document).dict(by_alias=by_alias)
        await self.db[model.__tablename__].insert_one(document)
        return document

    async def read_document(self, model: ModelMetaclass, oid: str) -> dict:
        try:
            document = await self.db[model.__tablename__].find_one({"_id": PyObjectId(oid)})
        except InvalidId:  # Second attempt if _id is not a BSON ObjectId
            document = await self.db[model.__tablename__].find_one({"_id": oid})
        if document is None:
            raise DocumentNotFound(oid)
        return document

    async def update_document(self, model: ModelMetaclass, oid: str, update: dict) -> dict:
        try:
            match = {"_id": PyObjectId(oid)}
        except InvalidId:
            match = {"_id": oid}
        update = {"$set": update}
        document = await self.db[model.__tablename__].find_one_and_update(match, update, return_document=True)
        if document is None:
            raise DocumentNotFound(oid)
        return document

    async def delete_document(self, model: ModelMetaclass, oid: str):
        try:
            delete = await self.db[model.__tablename__].delete_one({"_id": PyObjectId(oid)})
        except InvalidId:
            delete = await self.db[model.__tablename__].delete_one({"_id": oid})
        if delete.deleted_count == 0:
            raise DocumentNotFound(oid)

    async def count_documents(self, model: ModelMetaclass, q: BaseQuery) -> int:
        try:
            (total,) = await self.db[model.__tablename__].aggregate(q.count_pipeline()).to_list(1)
        except ValueError as err:
            # Special case: When the collection is empty total will be an empty list
            if "not enough values to unpack" not in str(err):
                raise  # pragma: no cover
            return 0
        return total["total"]

    async def read_multiple_documents(self, model: ModelMetaclass, q: BaseQuery) -> list[dict]:
        return [_ async for _ in self.db[model.__tablename__].aggregate(q.pipeline())]

    async def read_paginated_documents(self, model: ModelMetaclass, q: BasePaginatedQuery) -> dict:
        total = await self.count_documents(model, q)
        results = await self.db[model.__tablename__].aggregate(q.pipeline()).to_list(q.limit)
        return {
            "count": total,
            "next": q.page + 1 if q.skip + q.limit < total else None,
            "previous": q.page - 1 if q.page > 1 else None,
            "results": results,
        }
