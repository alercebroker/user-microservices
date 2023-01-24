import pytest
from fastapi import Query
from pydantic import dataclasses
from pydantic.error_wrappers import ValidationError

from query import BasePaginatedQuery, QueryRecipe


@dataclasses.dataclass
class MockQuery(BasePaginatedQuery):
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


def test_query_count_pipeline_does_not_include_skip():
    q = MockQuery(attr1="mock")

    assert all("skip" not in stage for stage in q.count_pipeline())


def test_query_count_pipeline_does_not_include_limit():
    q = MockQuery(attr1="mock")

    assert all("$limit" not in stage for stage in q.count_pipeline())


def test_query_pipeline_limits_according_to_parameters():
    q = MockQuery(attr1="mock", order_by="key", direction=-1, page=3, page_size=6)

    assert q.pipeline()[-1] == {"$limit": q.limit}


def test_query_pipeline_skips_according_to_parameters():
    q = MockQuery(attr1="mock", order_by="key", direction=-1, page=3, page_size=6)

    assert q.pipeline()[-2] == {"$skip": q.skip}


def test_query_pipeline_sorted_according_to_parameters():
    q = MockQuery(attr1="mock", order_by="key", direction=-1)

    assert q.pipeline()[-3] == {"$sort": {"key": -1}}


def test_query_pipeline_skip_is_calculated_from_page_size_and_page():
    page, size = 3, 6
    q = MockQuery(attr1="mock", order_by="key", direction=-1, page=page, page_size=size)

    assert q.skip == (page - 1) * size


def test_query_pipeline_limit_is_equal_to_page_size():
    q = MockQuery(attr1="mock", order_by="key", direction=-1, page=3, page_size=6)

    assert q.limit == 6


def test_query_pipeline_with_undefined_direction_fails():
    with pytest.raises(ValidationError, match="not a valid enumeration member"):
        MockQuery(attr1="mock", order_by="key", direction=0)


def test_query_pipeline_with_non_positive_page_fails():
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        MockQuery(attr1="mock", order_by="key", page=0)


def test_query_pipeline_with_non_positive_page_size_fails():
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        MockQuery(attr1="mock", order_by="key", page_size=0)
