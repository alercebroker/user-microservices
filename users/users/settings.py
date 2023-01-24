from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    port: int

class GoogleOAuthSettings(BaseSettings):
    client_id: str
    client_secret: str

    class Config:
        env_prefix = "google_"

class MongoSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str

    class Config:
        env_prefix = "mongodb_"


@lru_cache()
def get_server_settings():
    return Settings()


@lru_cache()
def get_google_settings():
    return GoogleOAuthSettings()

@lru_cache()
def get_mongo_settings():
    return MongoSettings()
