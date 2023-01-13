from typing import ClassVar

from bson import ObjectId
from pymongo import IndexModel
from pydantic import BaseModel, Field, main


def get_fields(model: type[BaseModel], by_alias: bool = True) -> tuple:
    """Get all fields in given model.

    Args:
        model (type[BaseModel]): Model to search for the fields
        by_alias (bool): Include fields by alias (if given) rather than name

    Returns:
        tuple[str]: Field names
    """
    return tuple(f.alias if by_alias else f.name for f in model.__fields__.values())


class DocumentNotFound(ValueError):
    def __init__(self, identifier):
        super().__init__(f"Document not found. ID: {identifier}")


class PyObjectId(ObjectId):
    """Custom type to allow for bson's ObjectId to be declared as types in pydantic models"""
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
    """Metaclass for MongoDB models

    This essentially allows for the storage of models intended to represent collections
    and access them as a property of the metaclass (`models`).

    This is mostly relevant only when initializing the database within the connection.

    The model is expected to have `__tablename__` as a class property, defining the
    name of the associated collection, and (optionally) `__indexes__`. The latter should
    be a list of `IndexModel` from pymongo and is used to initialize the indexes.

    If a collection name already exists, an error will be raised.

    If the model does not have `__tablename__`, it will be quietly ignored and a standard
    model will be added, without including it in `models`.
    """
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

        if not hasattr(cls, "__indexes__"):
            cls.__indexes__ = []
        mcs.__models.append(cls)
        return cls

    @property
    def models(self) -> tuple:
        return tuple(self.__models)


class SchemaMetaclass(MongoModelMetaclass):
    """Metaclass for creating schemas based on Mongo models

    This allows for inheriting from classes of type `MongoModelMetaclass` and
    using them as templates for schemas. Standard inheritance is possible, but it
    is also possible to remove fields from the parent. Field names defined in
    `__exclude__` (normally a set, but any iterable works) will be removed in the
    child class. **NOTE:** be mindful of validators when removing fields, since
    validators of removed fields or that depend on them will raise errors.

    Additionally, it is possible to use `__all_optional__` to force all fields to
    be optional, even those defined within the class proper. This includes removing
    any existing default factory and allowing the field to accept `None`. This is
    typically useful for generating PATCH schemas.

    The metaclass attribute `__is_schema__` is used to prevent `MongoModelMetaclass`
    from trying to add the schema to the models.
    """
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
    """Class that automatically handles the default `_id` from MongoDB

    If using your own value for `_id` it is recommended to still inherit from this class
    and simply override with a different type and default or default factory, given that the
    relevant metaclass for creating collections is already introduced here. Do not forget
    to set the alias to `_id` if overriding the field.
    """
    __tablename__: ClassVar[str]
    __indexes__: ClassVar[list[IndexModel]]

    id: PyObjectId = Field(default_factory=ObjectId, description="Unique identifier in DB", alias="_id")
