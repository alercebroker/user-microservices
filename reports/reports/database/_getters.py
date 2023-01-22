from functools import lru_cache

from db_handler import MongoConnection

from ..settings import MongoSettings


@lru_cache
def get_settings() -> MongoSettings:
    return MongoSettings()


@lru_cache
def get_connection() -> MongoConnection:
    return MongoConnection(get_settings())
