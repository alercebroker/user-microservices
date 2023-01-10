from .settings import MongoSettings
from db_handler.connection import MongoConnection


settings = MongoSettings()


def get_collection():
    connection = MongoConnection(settings.dict())
    connection.connect()
    try:
        yield connection.collection
    finally:
        connection.close()
