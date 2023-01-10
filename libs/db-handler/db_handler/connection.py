from collections import UserDict
from logging import getLogger
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = getLogger("db_handler")


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
            logger.error(f"Invalid configuration. Missing keys: {missing}")
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
    def __init__(self, config: dict | None = None):
        self.config = config
        self._client = None
        self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase | None:
        return self._db

    @property
    def config(self) -> _MongoConfig | None:
        return self.__config

    @config.setter
    def config(self, config: dict | None):
        self.__config = _MongoConfig(config) if config else None

    def connect(self, config: dict | None = None):
        """Establishes connection to a database and initializes a session.

        Parameters
        ----------
        config : dict
            Database configuration. For example:

            .. code-block:: python

                config = {
                    "HOST": "host",
                    "USERNAME": "username",
                    "PASSWORD": "pwd",
                    "PORT": 27017, # mongo typically runs on port 27017.
                                   # Notice that we use an int here.
                    "DATABASE": "database",
                    "AUTH_SOURCE": "admin" # could be admin or the same as DATABASE
                }
        """
        if self._client:
            logger.warning("Existing connection to MongoDB will be closed")
            self.close()
        if config:
            self.config = config
        if self.config is None:
            logger.error("Cannot connect: No configuration provided for client")
            raise ValueError("No configuration provided for client")
        self._client = AsyncIOMotorClient(**self.config)
        logger.info(f"Connected to MongoDB at {self.config['host']}:{self.config['port']}")
        self._db = self._client[self.config.db]
        logger.debug(f"Connected to database {self.config.db}")

    def close(self):
        self._client.close()
        logger.info("Connection to MongoDB closed")
        self._client = None
        self._db = None
