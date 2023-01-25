import pytest
from pydantic import BaseModel, Field

from query import field_enum_factory


def test_field_enum_by_alias():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = field_enum_factory(MockModel, by_alias=True)
    assert output_enum.field1 == "alias1"
    assert output_enum.field2 == "field2"


def test_field_enum_by_name():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = field_enum_factory(MockModel, by_alias=False)
    assert output_enum.field1 == "field1"
    assert output_enum.field2 == "field2"


def test_field_enum_with_exclusion():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = field_enum_factory(MockModel, exclude={"field1"})
    with pytest.raises(AttributeError, match="field1"):
        output_enum.field1
    assert output_enum.field2 == "field2"
