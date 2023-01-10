from collections import UserDict
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


# Aliases (this avoids making motor a hard dependency por the APIs)
MongoDatabase = AsyncIOMotorDatabase
MongoCollection = AsyncIOMotorCollection


class _MongoConfig(UserDict):
    """Special dictionary used to parse configuration dictionaries for mongodb.

    The required keys are described in `REQUIRED_KEYS`, but can come with any
    capitalization.

    All keys are converted from `snake_case` to `lowerCamelCase` format, as
    used by `motor` (python asynchronous driver for MongoDB). The special key
    `database` is removed from the dictionary proper, but can be accessed
    through the property `db`.
    """

    REQUIRED_KEYS = {"host", "username", "password", "port", "database", "collection"}

    def __init__(self, seq=None, **kwargs):
        super().__init__(seq, **kwargs)
        if self.REQUIRED_KEYS.difference(self.keys()):
            missing = ", ".join(
                key.upper() for key in self.REQUIRED_KEYS.difference(self.keys())
            )
            raise ValueError(f"Invalid configuration. Missing keys: {missing}")
        self._db = self.pop("database")
        self._collection = self.pop("collection")

    @property
    def db(self) -> str:
        """str: database name"""
        return self._db

    @property
    def collection(self) -> str:
        """str: collection name"""
        return self._collection

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
    def db(self) -> MongoDatabase:
        return self._client[self._config.db]

    @property
    def collection(self) -> MongoCollection:
        return self.db[self._config.collection]

    def __del__(self):
        self.close()

    def connect(self):
        """Establishes connection to a database and initializes a session."""
        self._client = AsyncIOMotorClient(connect=True, **self._config)

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
