from functools import lru_cache

from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str


class Settings(BaseSettings):
    alerts_api_url: str
    root_path: str = ""
    mongodb: MongoSettings

    class Config:
        env_nested_delimiter = "_"
        env_file = ".env.test"


@lru_cache
def get_settings():
    return Settings()
