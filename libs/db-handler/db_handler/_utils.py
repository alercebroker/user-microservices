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
    _CLONE_NAMESPACE = {"__annotations__": {}, "__module__": "pydantic.main"}
    collections = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        try:
            collection = cls.__tablename__
        except AttributeError:
            return cls

        if collection in mcs.collections:
            if namespace == mcs._CLONE_NAMESPACE:
                # FastAPI creates clones of the models for the endpoints
                # Every time a clone is creates, this __new__ runs
                # The namespace is NOT copied and is unique for the clones
                return cls
            raise ValueError(f"Duplicate collection name: {collection}")

        mcs.collections[collection] = getattr(cls, "__indexes__", None)

        return cls


class BaseModelWithId(BaseModel, metaclass=MongoModelMetaclass):
    """Class that automatically handles `_id` from MongoDB"""
    __tablename__: ClassVar[str]
    __indexes__: ClassVar[list[IndexModel]]

    id: PyObjectId = Field(default_factory=ObjectId, description="Unique identifier in DB", alias="_id")

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda x: x.isoformat()}
