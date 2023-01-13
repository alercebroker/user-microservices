from typing import ClassVar

from bson import ObjectId
from pymongo import IndexModel
from pydantic import BaseModel, Field, main


class DocumentNotFound(ValueError):
    def __init__(self, identifier):
        super().__init__(f"Document not found. ID: {identifier}")


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
    __models = []

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        try:
            tablename = cls.__tablename__
        except AttributeError:
            return cls

        if any(tablename == model.__tablename__ for model in mcs.__models):
            if mcs.__is_schema__:
                # Prevents schemas from adding tables
                return cls
            raise ValueError(f"Duplicate collection name: {tablename}")

        mcs.__models.append(cls)
        return cls

    @property
    def models(self) -> tuple:
        return tuple(self.__models)


class SchemaMetaclass(MongoModelMetaclass):
    """Metaclass for creating schemas based on Mongo models"""
    __is_schema__ = True

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if not hasattr(cls, "__exclude__"):
            cls.__exclude__ = set()
        if not hasattr(cls, "__all_optional__"):
            cls.__all_optional__ = False

        cls.__fields__ = {k: v for k, v in cls.__fields__.items() if k not in cls.__exclude__}
        if not cls.__all_optional__:
            return cls
        for field in cls.__fields__.values():
            field.required = False
            field.default_factory = None
            field.default = None
        return cls


class BaseModelWithId(BaseModel, metaclass=MongoModelMetaclass):
    """Class that automatically handles `_id` from MongoDB"""
    __tablename__: ClassVar[str]
    __indexes__: ClassVar[list[IndexModel]]

    id: PyObjectId = Field(default_factory=ObjectId, description="Unique identifier in DB", alias="_id")
