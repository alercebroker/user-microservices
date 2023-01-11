from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str
    collection: str

    class Config:
        env_prefix = "mongodb_"
        env_file = ".env"
