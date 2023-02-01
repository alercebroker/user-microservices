import pytest
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

from db_handler import ModelMetaclass, SchemaMetaclass, PyObjectId


@pytest.fixture
def empty_models():
    yield
    ModelMetaclass.__models__.clear()


def test_pyobjectid_can_be_used_as_pydantic_model_type_and_converts_automatically():
    class TestModel(BaseModel):
        id: PyObjectId

    model = TestModel(id="123456789012345678901234")
    assert model.id == PyObjectId("123456789012345678901234")


def test_pyobjectid_can_be_used_as_pydantic_model_type_and_validates_automatically():
    class TestModel(BaseModel):
        id: PyObjectId

    with pytest.raises(ValidationError, match="Not a valid ObjectId"):
        TestModel(id="invalid")


def test_model_metaclass_stores_created_model_if_tablename_is_defined(empty_models):
    assert ModelMetaclass.__models__ == set()

    class TestModel(BaseModel, metaclass=ModelMetaclass):
        __tablename__ = "test"

    assert ModelMetaclass.__models__ == {TestModel}


def test_model_metaclass_stores_ignores_model_if_tablename_is_not_defined(empty_models):
    assert ModelMetaclass.__models__ == set()

    class TestModel(BaseModel, metaclass=ModelMetaclass):
        pass

    assert ModelMetaclass.__models__ == set()
    assert not hasattr(TestModel, '__indexes__')


def test_model_metaclass_adds_empty_list_as_indexes_if_indexes_are_not_defined(empty_models):
    assert ModelMetaclass.__models__ == set()

    class TestModel(BaseModel, metaclass=ModelMetaclass):
        __tablename__ = "test"

    assert ModelMetaclass.__models__ == {TestModel}
    assert TestModel.__indexes__ == []


def test_model_metaclass_fails_if_it_has_duplicate_tablename(empty_models):
    assert ModelMetaclass.__models__ == set()

    class TestModel(BaseModel, metaclass=ModelMetaclass):
        __tablename__ = "test"

    with pytest.raises(ValueError, match="Duplicate collection name"):
        class TestModel2(BaseModel, metaclass=ModelMetaclass):
            __tablename__ = "test"


def test_schema_metaclass_ignores_duplicate_tablenames(empty_models):
    assert ModelMetaclass.__models__ == set()

    class TestModel(BaseModel, metaclass=ModelMetaclass):
        __tablename__ = "test"

    class TestModel2(BaseModel, metaclass=SchemaMetaclass):
        __tablename__ = "test"

    assert ModelMetaclass.__models__ == {TestModel}


def test_schema_metaclass_excludes_required_fields():
    class TestModel(BaseModel, metaclass=SchemaMetaclass):
        field1: str
        field2: int

    class TestModel2(TestModel):
        __exclude__ = {"field1"}

    assert "field1" not in TestModel2.__fields__


def test_schema_metaclass_makes_all_fields_optional_if_required():
    class TestModel(BaseModel, metaclass=SchemaMetaclass):
        field1: str
        field2: int

    class TestModel2(TestModel):
        __all_optional__ = True

    assert TestModel.__fields__["field1"].required  # Make sure original model is required
    assert TestModel.__fields__["field2"].required  # Make sure original model is required

    assert TestModel2.__fields__["field1"].required is False
    assert TestModel2.__fields__["field2"].required is False
