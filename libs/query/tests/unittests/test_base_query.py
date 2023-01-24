import pytest
from fastapi import Query
from pydantic import dataclasses
from pydantic.error_wrappers import ValidationError

from query import BaseQuery, QueryRecipe


@dataclasses.dataclass
class MockQuery(BaseQuery):
    attr1: str = Query()
    attr2: int | None = Query()

    recipes = (QueryRecipe("field1", ["$op1"], ["attr1"]), QueryRecipe("field2", ["$op2"], ["attr2"]))


def test_query_creation_with_default():
    q = MockQuery(attr1="mock")

    assert q.attr1 == "mock"
    assert q.attr2 is None


def test_query_creation_without_default():
    q = MockQuery(attr1="mock", attr2=1)

    assert q.attr1 == "mock"
    assert q.attr2 == 1


def test_query_creation_missing_mandatory_fails():
    with pytest.raises(ValidationError, match="field required"):
        MockQuery()


def test_query_creation_with_castable_type_casts_to_correct_type():
    q = MockQuery(attr1=3)

    assert q.attr1 == "3"


def test_query_pipeline_builds_all_filters():
    q = MockQuery(attr1="mock", attr2=1)

    assert q.pipeline() == [{"$match": {"field1": {"$op1": "mock"}, "field2": {"$op2": 1}}}]


def test_query_pipeline_ignores_none_values():
    q = MockQuery(attr1="mock")

    assert q.pipeline() == [{"$match": {"field1": {"$op1": "mock"}}}]


def test_query_count_pipeline_finishes_in_count_stage_with_total_field():
    q = MockQuery(attr1="mock")

    assert q.count_pipeline()[-1] == {"$count": "total"}
