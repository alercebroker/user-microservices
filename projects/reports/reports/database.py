from .settings import MongoSettings
from db_handler.connection import MongoConnection


settings = MongoSettings()
connection = MongoConnection(settings.dict())
