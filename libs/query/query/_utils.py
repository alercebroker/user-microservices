from enum import IntEnum
from typing import ClassVar, NamedTuple, Literal

from fastapi import Query
from pydantic import BaseModel, dataclasses


def get_fields(model: type[BaseModel], by_alias: bool = True, *, exclude=None) -> tuple[str]:
    exclude = exclude or set()
    return tuple(f.alias if by_alias else f.name for f in model.__fields__.values() if f.name not in exclude)


class Direction(IntEnum):
    ascending = 1
    descending = -1


class QueryRecipe(NamedTuple):
    """Recipe to generate a filter for mongo queries (either in a `$match` aggregation pipeline
    stage or in `find`/`find_one` methods).

    The length of `operators` and `attributes` should be the same, although this is not enforced.

    Attributes:
        field (str): Field in document to be queried
        operators (list[str]): Mongo operators used for filtering
        attributes (list[str]): Class attribute names containing values for the operators
    """

    field: str
    operators: list[str]
    attributes: list[str]

    def pair(self, q) -> tuple[str, dict]:
        """Generates pair with field name and the mongo dictionary used for filtering according to the
        recipe.

        This method searches for the attribute values inside the input dataclass object. As such, it
        expects all the defined `attributes` to be present. Any value of `None` will be ignored.

        Args:
            q (object): Instance of a dataclass to search for attribute values

        Returns:
            tuple[str, dict]: Field name and dictionary for filtering over that field in mongo
        """
        values = (getattr(q, attr) for attr in self.attributes)
        condition = {op: val for op, val in zip(self.operators, values) if val is not None}
        return self.field, condition


@dataclasses.dataclass
class BaseQuery:
    """Basic class for generating query parameters.

    The methods are based on generating pipelines for MongoDB usage.

    Attributes:
        recipes (tuple[QueryRecipe]): Recipes for filter creation
    """

    recipes: ClassVar[tuple[QueryRecipe]]

    @staticmethod
    def _project_without_id(field):
        return {k: False if k == "_id" else True for k in field}

    def _basic_pipeline(self) -> list[dict]:
        """All stages for generating documents of interest. Should not include sort, skip, etc."""
        return [{"$match": {k: v for k, v in (r.pair(self) for r in self.recipes) if v}}]

    def pipeline(self) -> list[dict]:
        """Aggregation pipeline for mongo.

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        return self._basic_pipeline()

    def count_pipeline(self) -> list[dict]:
        """Aggregation pipeline for mongo to count documents.

        The output of the aggregation will be a single document with a single field called `total`,
        which has the total number of elements.

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        return self._basic_pipeline() + [{"$count": "total"}]


@dataclasses.dataclass
class BaseSortedQuery(BaseQuery):
    """Base class for handling typical queries that require sorting.

    Subclasses MUST implement instructions for `order_by`.
    This mainly refers to adding the available options, a default and proper description.
    """

    order_by: Literal["NOT_IMPLEMENTED"]
    direction: Direction = Query(-1, description="Sort by ascending or descending values")

    def pipeline(self) -> list[dict]:
        """Aggregation pipeline for mongo.

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        return super().pipeline() + [{"$sort": {self.order_by: self.direction}}]


@dataclasses.dataclass
class BasePaginatedQuery(BaseSortedQuery):
    """Base class for handling typical queries on reports with pagination."""

    page: int = Query(1, description="Page for paginated results", ge=1)
    page_size: int = Query(10, description="Number of reports per page", ge=1)

    @property
    def skip(self) -> int:
        """Number of documents to skip"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Number of documents per page"""
        return self.page_size

    def pipeline(self) -> list[dict]:
        return super().pipeline() + [{"$skip": self.skip}, {"$limit": self.limit}]
