import logging
from collections import UserDict
from functools import wraps
from typing import Any

from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
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
    logger = logging.getLogger("connection")

    def __init__(self, **kwargs):
        self._config = _MongoConfig(kwargs)
        self._client = None

    @staticmethod
    def _error_logger(method):
        """Decorator for coroutines methods.

        Will log the exception with stack info except for `DuplicateKeyError` and `DocumentNotFound` errors.
        """

        @wraps(method)
        async def wrapper(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except DuplicateKeyError:
                raise  # pragma: no cover
            except DocumentNotFound:
                raise  # pragma: no cover
            except Exception as exc:
                self.logger.error(str(exc), stack_info=True)
                raise

        return wrapper

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self._client[self._config.db]

    @_error_logger
    async def connect(self):
        self._client = AsyncIOMotorClient(**self._config)
        self.logger.debug(f"Connected to: mongodb://{self._config['host']}:{self._config['port']}.")

    @_error_logger
    async def close(self):
        self.logger.debug(f"Closing connection to MongoDB.")
        self._client.close()
        self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @_error_logger
    async def create_db(self):
        for cls in ModelMetaclass.__models__:
            if cls.__indexes__:
                name = cls.__tablename__
                await self.db[name].create_indexes(cls.__indexes__)

    @_error_logger
    async def drop_db(self):
        self.logger.info(f"Dropping database: {self._config.db}.")
        await self._client.drop_database(self.db)

    @staticmethod
    def _parse_oid(oid):
        try:
            return PyObjectId(oid)
        except InvalidId:
            return oid

    @classmethod
    def _check(cls, doc, oid):
        if doc is None:
            raise DocumentNotFound(oid)
        return doc

    @_error_logger
    async def create_document(self, model: ModelMetaclass, document: dict) -> dict:
        """Fields in `document` not defined in `model` will be quietly ignored"""
        document = model(**document).dict(by_alias=True)
        await self.db[model.__tablename__].insert_one(document)
        return document

    @_error_logger
    async def read_document(self, model: ModelMetaclass, oid: str) -> dict | None:
        oid = self._parse_oid(oid)
        return self._check(await self.db[model.__tablename__].find_one({"_id": oid}), oid)

    @_error_logger
    async def update_document(self, model: ModelMetaclass, oid: str, update: dict) -> dict | None:
        """Will quietly work even if `update` includes fields not defined in `model`"""
        modify = ({"_id": self._parse_oid(oid)}, {"$set": update})
        return self._check(await self.db[model.__tablename__].find_one_and_update(*modify, return_document=True), oid)

    @_error_logger
    async def delete_document(self, model: ModelMetaclass, oid: str) -> dict | None:
        oid = self._parse_oid(oid)
        return self._check(await self.db[model.__tablename__].find_one_and_delete({"_id": oid}), oid)

    @_error_logger
    async def count_documents(self, model: ModelMetaclass, q: BaseQuery) -> int:
        try:
            (total,) = await self.db[model.__tablename__].aggregate(q.count_pipeline()).to_list(1)
        except ValueError as err:
            # Special case: When the collection is empty total will be an empty list
            if "not enough values to unpack" not in str(err):
                raise  # pragma: no cover
            return 0
        return total["total"]

    @_error_logger
    async def read_documents(self, model: ModelMetaclass, q: BaseQuery) -> list[dict]:
        return await self.db[model.__tablename__].aggregate(q.pipeline()).to_list(None)
