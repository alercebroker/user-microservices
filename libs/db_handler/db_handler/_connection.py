from collections import UserDict
from typing import Any

from asyncio import Future
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
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
    def __init__(self, **kwargs):
        self._config = _MongoConfig(kwargs)
        self._client = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self._client[self._config.db]

    async def connect(self):
        self._client = AsyncIOMotorClient(connect=True, **self._config)

    async def close(self):
        self._client.close()
        self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_db(self):
        for cls in ModelMetaclass.__models__:
            if cls.__indexes__:
                await self.db[cls.__tablename__].create_indexes(cls.__indexes__)

    async def drop_db(self):
        await self._client.drop_database(self.db)

    @staticmethod
    def _parse_oid(oid):
        try:
            return PyObjectId(oid)
        except InvalidId:
            return oid

    @staticmethod
    def _check(doc, oid):
        if doc is None:
            raise DocumentNotFound(oid)
        return doc

    async def create_document(self, model: ModelMetaclass, document: dict) -> dict:
        """Fields in `document` not defined in `model` will be quietly ignored"""
        document = model(**document).dict(by_alias=True)
        await self.db[model.__tablename__].insert_one(document)
        return document

    async def read_document(self, model: ModelMetaclass, oid: str) -> Future:
        oid = self._parse_oid(oid)
        return self._check(await self.db[model.__tablename__].find_one({"_id": oid}), oid)

    async def update_document(self, model: ModelMetaclass, oid: str, update: dict) -> Future:
        """Will quietly work even if `update` includes fields not defined in `model`"""
        oid = self._parse_oid(oid)
        return self._check(await self.db[model.__tablename__].find_one_and_update({"_id": oid}, {"$set": update}, return_document=True), oid)

    async def delete_document(self, model: ModelMetaclass, oid: str) -> Future:
        oid = self._parse_oid(oid)
        return self._check(await self.db[model.__tablename__].find_one_and_delete({"_id": oid}), oid)

    async def count_documents(self, model: ModelMetaclass, q: BaseQuery) -> int:
        try:
            (total,) = await self.db[model.__tablename__].aggregate(q.count_pipeline()).to_list(1)
        except ValueError as err:
            # Special case: When the collection is empty total will be an empty list
            if "not enough values to unpack" not in str(err):
                raise  # pragma: no cover
            return 0
        return total["total"]

    async def read_documents(self, model: ModelMetaclass, q: BaseQuery) -> list[dict]:
        return [_ async for _ in self.db[model.__tablename__].aggregate(q.pipeline())]

    async def paginate_documents(self, model: ModelMetaclass, q: BasePaginatedQuery) -> list[dict]:
        return await self.db[model.__tablename__].aggregate(q.pipeline()).to_list(q.limit)
