from functools import lru_cache

from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str

    class Config:
        env_prefix = "mongodb_"
        env_file = ".env.test"


class ExtraSettings(BaseSettings):
    alerts_api_url: str

    class Config:
        env_file = ".env.test"


@lru_cache
def get_settings() -> MongoSettings:
    return MongoSettings()
