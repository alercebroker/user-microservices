from pydantic import BaseModel, Field

from query import get_fields


def test_field_enum_by_alias():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = get_fields(MockModel, by_alias=True)
    assert output_enum == ("alias1", "field2")


def test_field_enum_by_name():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = get_fields(MockModel, by_alias=False)
    assert output_enum == ("field1", "field2")


def test_field_enum_with_exclusion():
    class MockModel(BaseModel):
        field1: str = Field(..., alias="alias1")
        field2: str

    output_enum = get_fields(MockModel, exclude={"field1"})
    assert output_enum == ("field2",)
