from functools import lru_cache

from db_handler import MongoConnection

from ..settings import get_settings


@lru_cache
def get_connection() -> MongoConnection:
    return MongoConnection(get_settings().dict())
