from collections import UserDict
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCursor
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult, UpdateResult
from pydantic import BaseSettings

from ._utils import MongoModelMetaclass


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
        """Establishes connection to a database and initializes a session."""
        self._client = AsyncIOMotorClient(connect=True, **self._config)

    async def close(self):
        self._client.close()
        self._client = None

    async def create_db(self):
        for cls in MongoModelMetaclass.__models__:
            if cls.__indexes__:
                await self.db[cls.__tablename__].create_indexes(cls.__indexes__)

    async def drop_db(self):
        await self._client.drop_database(self._config.db)

    async def find_one(self, model: MongoModelMetaclass, *args, **kwargs) -> dict | None:
        return await self.db[model.__tablename__].find_one(*args, **kwargs)

    async def find_one_and_delete(self, model: MongoModelMetaclass, *args, **kwargs) -> dict | None:
        return await self.db[model.__tablename__].find_one_and_delete(*args, **kwargs)

    async def find_one_and_replace(self, model: MongoModelMetaclass, *args, **kwargs) -> dict | None:
        return await self.db[model.__tablename__].find_one_and_replace(*args, **kwargs)

    async def find_one_and_update(self, model: MongoModelMetaclass, *args, **kwargs) -> dict | None:
        return await self.db[model.__tablename__].find_one_and_update(*args, **kwargs)

    def find(self, model: MongoModelMetaclass, *args, **kwargs) -> AsyncIOMotorCursor:
        return self.db[model.__tablename__].find(*args, **kwargs)

    async def delete_one(self, model: MongoModelMetaclass, *args, **kwargs) -> DeleteResult:
        return await self.db[model.__tablename__].delete_one(*args, **kwargs)

    async def delete_many(self, model: MongoModelMetaclass, *args, **kwargs) -> DeleteResult:
        return await self.db[model.__tablename__].delete_many(*args, **kwargs)

    async def insert_one(self, model: MongoModelMetaclass, *args, **kwargs) -> InsertOneResult:
        return await self.db[model.__tablename__].insert_one(*args, **kwargs)

    async def insert_many(self, model: MongoModelMetaclass, *args, **kwargs) -> InsertManyResult:
        return await self.db[model.__tablename__].insert_many(*args, **kwargs)

    async def update_one(self, model: MongoModelMetaclass, *args, **kwargs) -> UpdateResult:
        return await self.db[model.__tablename__].update_one(*args, **kwargs)

    async def update_many(self, model: MongoModelMetaclass, *args, **kwargs) -> UpdateResult:
        return await self.db[model.__tablename__].update_many(*args, **kwargs)

    def aggregate(self, model: MongoModelMetaclass, *args, **kwargs) -> AsyncIOMotorCursor:
        return self.db[model.__tablename__].aggregate(*args, **kwargs)