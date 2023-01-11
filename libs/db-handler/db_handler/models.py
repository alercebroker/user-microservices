from datetime import datetime
from typing import ClassVar

from bson import ObjectId
from pydantic import BaseModel, Field


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


class BaseModelWithId(BaseModel):
    __tablename__: ClassVar[str]

    id: PyObjectId = Field(default_factory=ObjectId, description="Unique identifier in DB", alias="_id")

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda x: x.isoformat()}
