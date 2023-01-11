from collections import UserDict
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCursor
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult, UpdateResult

from .models import BaseModelWithId


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
            missing = ", ".join(
                key.upper() for key in self.REQUIRED_KEYS.difference(self.keys())
            )
            raise ValueError(f"Invalid configuration. Missing keys: {missing}")
        self._db = self.pop("database")

    @property
    def db(self) -> str:
        """str: database name"""
        return self._db

    def __setitem__(self, key: str, value: Any):
        """Converts keys from (case-insensitive) `snake_case` to `lowerCamelCase`"""
        klist = [
            w.lower() if i == 0 else w.title() for i, w in enumerate(key.split("_"))
        ]
        super().__setitem__("".join(klist), value)


class MongoConnection:
    def __init__(self, config: dict):
        self._config = _MongoConfig(config)
        self._client = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return self._client[self._config.db]

    async def connect(self):
        """Establishes connection to a database and initializes a session."""
        self._client = AsyncIOMotorClient(connect=True, **self._config)

    async def close(self):
        if self._client is None:
            raise ValueError("Connection is not established")
        self._client.close()
        self._client = None

    def find_one(self, model: type[BaseModelWithId], *args, **kwargs) -> dict | None:
        return self.db[model.__tablename__].find_one(*args, **kwargs)

    def find(self, model: type[BaseModelWithId], *args, **kwargs) -> AsyncIOMotorCursor:
        return self.db[model.__tablename__].find(*args, **kwargs)

    def delete_one(self, model: type[BaseModelWithId], *args, **kwargs) -> DeleteResult:
        return self.db[model.__tablename__].delete_one(*args, **kwargs)

    def delete_many(self, model: type[BaseModelWithId], *args, **kwargs) -> DeleteResult:
        return self.db[model.__tablename__].delete_many(*args, **kwargs)

    def insert_one(self, model: type[BaseModelWithId], *args, **kwargs) -> InsertOneResult:
        return self.db[model.__tablename__].insert_one(*args, **kwargs)

    def insert_many(self, model: type[BaseModelWithId], *args, **kwargs) -> InsertManyResult:
        return self.db[model.__tablename__].insert_many(*args, **kwargs)

    def update_one(self, model: type[BaseModelWithId], *args, **kwargs) -> UpdateResult:
        return self.db[model.__tablename__].update_one(*args, **kwargs)

    def update_many(self, model: type[BaseModelWithId], *args, **kwargs) -> UpdateResult:
        return self.db[model.__tablename__].update_many(*args, **kwargs)

    def aggregate(self, model: type[BaseModelWithId], *args, **kwargs) -> AsyncIOMotorCursor:
        return self.db[model.__tablename__].aggregate(*args, **kwargs)
