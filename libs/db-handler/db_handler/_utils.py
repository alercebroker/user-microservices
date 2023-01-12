from datetime import datetime, timezone
from typing import ClassVar

from bson import ObjectId
from pymongo import IndexModel
from pydantic import BaseModel, Field, main


def now_utc() -> datetime:
    """Return current time at UTC"""
    return datetime.now(timezone.utc)


class PyObjectId(ObjectId):
    """Class that allows for ObjectId to be use in pydantic models as string"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Not a valid ObjectID: {v}")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoModelMetaclass(main.ModelMetaclass):
    """Metaclass for MongoDB models"""
    __CLONE_NAMESPACE = {"__annotations__": {}, "__module__": "pydantic.main"}
    __models = []

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        try:
            name = cls.__tablename__
        except AttributeError:
            return cls

        if any(name == model.__tablename__ for model in mcs.__models):
            if namespace == mcs.__CLONE_NAMESPACE:
                # FastAPI creates clones of the models for the endpoints
                # Every time a clone is creates, this __new__ runs
                # The namespace is NOT copied and the above can identify a clone
                return cls
            raise ValueError(f"Duplicate collection name: {name}")

        mcs.__models.append(cls)
        return cls

    @property
    def models(mcs) -> tuple:
        return tuple(mcs.__models)


class BaseModelWithId(BaseModel, metaclass=MongoModelMetaclass):
    """Class that automatically handles `_id` from MongoDB"""
    __tablename__: ClassVar[str]
    __indexes__: ClassVar[list[IndexModel]]

    id: PyObjectId = Field(default_factory=ObjectId, description="Unique identifier in DB", alias="_id")

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda x: x.isoformat()}
