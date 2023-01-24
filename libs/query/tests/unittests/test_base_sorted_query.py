import pytest
from fastapi import Query
from pydantic import dataclasses
from pydantic.error_wrappers import ValidationError

from query import BaseSortedQuery, QueryRecipe


@dataclasses.dataclass
class MockQuery(BaseSortedQuery):
    order_by: str = Query("default")
    attr1: str = Query()
    attr2: int | None = Query()

    recipes = (QueryRecipe("field1", ["$op1"], ["attr1"]), QueryRecipe("field2", ["$op2"], ["attr2"]))


def test_query_count_pipeline_finishes_in_count_stage_with_total_field():
    q = MockQuery(attr1="mock")

    assert q.count_pipeline()[-1] == {"$count": "total"}


def test_query_count_pipeline_does_not_include_sort():
    q = MockQuery(attr1="mock")

    assert all("$sort" not in stage for stage in q.count_pipeline())


def test_query_pipeline_sorted_according_to_parameters():
    q = MockQuery(attr1="mock", order_by="key", direction=-1)

    assert q.pipeline()[-1] == {"$sort": {"key": -1}}


def test_query_pipeline_with_undefined_direction_fails():
    with pytest.raises(ValidationError, match="not a valid enumeration member"):
        MockQuery(attr1="mock", order_by="key", direction=0)
