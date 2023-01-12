from datetime import datetime
from typing import Literal, Pattern, NamedTuple, ClassVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from .models import Report, ReportByObject, ReportByDay


def get_fields(model: type[BaseModel], alias: bool = True) -> tuple[str]:
    """Get all fields in the model.

    Args:
        model (type[BaseModel]): Model to search for the fields
        alias (bool): Include fields by alias (if given) rather than name

    Returns:
        tuple[str]: Field names
    """
    return tuple(model.schema(alias).get("properties"))


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


@dataclass
class BaseQuery:
    """Base class for handling typical queries on reports.

    While defined here, subclasses should implement instructions for `order_by`.
    This mainly refers to adding the available options, a default and proper description.

    Attributes:
        recipes (tuple[QueryRecipe]): Recipes for filter creation
    """
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    order_by: Literal[""] = Query("", description="NEEDS TO BE OVERRIDEN!!")
    direction: Literal["1", "-1"] = Query("-1", description="Sort by ascending or descending values")

    recipes: ClassVar[tuple[QueryRecipe]] = (
        QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        QueryRecipe("object", ["$regex"], ["object"])
    )

    def _match(self) -> list[dict]:
        """Generates match stage for pipeline"""
        return [{"$match": {k: v for k, v in (r.pair(self) for r in self.recipes) if v}}]

    def _sort(self) -> list[dict]:
        """Generates sort stage for pipeline"""
        return [{"$sort": {self.order_by: int(self.direction)}}] if self.order_by else []

    def _query_pipeline(self) -> list[dict]:
        """All stages for generating documents of interest. Should not include sort, skip, etc."""
        return self._match()

    def pipeline(self) -> list[dict]:
        """Aggregation pipeline for mongo.

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        return self._query_pipeline() + self._sort()

    def count_pipeline(self) -> list[dict]:
        """Aggregation pipeline for mongo to count documents.

        The output of the aggregation will be a single document with a single field called `total`,
        which has the total number of elements.

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        return self._query_pipeline() + [{"$count": "total"}]


@dataclass
class BasePaginatedQuery(BaseQuery):
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


@dataclass
class QueryByReport(BasePaginatedQuery):
    """Queries that will return individual reports, directly as they come from the database."""
    order_by: Literal[get_fields(Report)] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(BasePaginatedQuery):
    """Queries that will return reports grouped by object."""
    order_by: Literal[get_fields(ReportByObject)] = Query("last_date", description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {
            "_id": "$object",
            "first_date": {"$min": "$date"},
            "last_date": {"$max": "$date"},
            "users": {"$addToSet": "$owner"},
            "source": {"$addToSet": "$source"},
            "report_type": {"$addToSet": "$report_type"},
            "count": {"$count": {}}
        }
        return super()._query_pipeline() + [{"$group": group}, {"$set": {"object": "$_id"}}]


@dataclass
class QueryByDay(BaseQuery):
    """Queries that return number of reports per day."""
    order_by: Literal[get_fields(ReportByDay)] = Query("day", description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {
            "_id": {
                "$dateTrunc": {
                    "date": {"$toDate": "$date"},
                    "unit": "day"
                }
            },
            "count": {"$count": {}}
        }
        return super()._query_pipeline() + [{"$group": group}, {"$set": {"day": "$_id"}}]
