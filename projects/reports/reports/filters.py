from datetime import datetime
from typing import Literal, Pattern, NamedTuple, ClassVar

from fastapi import Query
from pydantic.dataclasses import dataclass

from .models import Report, ReportByObject, ReportByDay


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
    page: int = Query(1, description="Page for paginated results", ge=1)
    page_size: int = Query(10, description="Number of reports per page", ge=1)
    order_by: Literal[""] = Query("", description="NEEDS TO BE OVERRIDEN!!")
    direction: Literal["1", "-1"] = Query("-1", description="Sort by ascending or descending values")

    recipes: ClassVar[tuple[QueryRecipe]] = (
        QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        QueryRecipe("object", ["$regex"], ["object"])
    )

    def _match(self) -> dict:
        """Generates full mongo filter for finding elements"""
        return {k: v for k, v in (r.pair(self) for r in self.recipes) if v}

    def __sort(self) -> dict | None:
        """Dictionary for mongo sorting. Will be `None` if there is no element to order by"""
        return {self.order_by: int(self.direction)} if self.order_by else None

    def skip(self) -> int:
        """Number of documents to skip"""
        return (self.page - 1) * self.page_size

    def limit(self) -> int:
        """Number of documents per page"""
        return self.page_size

    def _filter(self) -> list[dict]:
        """Pipeline stages for mongo aggregation that select/modify requested documents"""
        return [{"$match": self._match()}]

    def __page(self) -> list[dict]:
        """Pipeline stages for sorting (if valid) and pagination"""
        sort = [{"$sort": self.__sort()}] if self.__sort() else []
        return sort + [{"$skip": self.skip()}, {"$limit": self.limit()}]

    def pipeline(self, paginate: bool = True, count: bool = False) -> list[dict]:
        """Aggregation pipeline for mongo.

        When using `count`, note that the result of the pipeline is a single document
        with a single field called `total`, which contains the number of documents queried.
        Note that, if used together with `paginate`, it will return only the number of
        documents in the current page.

        Args:
            paginate (bool): Whether to include sorting and pagination stages
            count (bool): Whether to finish with a counting stage

        Returns:
            list[dict]: List with stages for mongo pipeline
        """
        paginate = self.__page() if paginate else []
        count = [{"$count": "total"}] if count else []
        return self._filter() + paginate + count


@dataclass
class QueryByReport(BaseQuery):
    """Queries that will return individual reports, directly as they come from the database."""
    order_by: Literal[Report.get_fields()] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(BaseQuery):
    """Queries that will return reports grouped by object."""
    order_by: Literal[ReportByObject.get_fields()] = Query("last_date", description="Field to sort by")

    @staticmethod
    def _group() -> dict:
        """Instructions for the `$group` stage of the pipeline."""
        return {
            "_id": "$object",
            "first_date": {"$min": "$date"},
            "last_date": {"$max": "$date"},
            "users": {"$addToSet": "$owner"},
            "source": {"$addToSet": "$source"},
            "report_type": {"$addToSet": "$report_type"},
            "count": {"$count": {}}
        }

    @staticmethod
    def _set() -> dict:
        """Instructions for the `$set` stage of the pipeline"""
        return {"object": "$_id"}

    def _filter(self) -> list[dict]:
        return [{"$match": self._match()}, {"$group": self._group()}, {"$set": self._set()}]


@dataclass
class QueryByDay(QueryByObject):
    """Queries that return number of reports per day."""
    order_by: Literal[ReportByDay.get_fields()] = Query("day", description="Field to sort by")

    @staticmethod
    def _group() -> dict:
        return {
            "_id": {"$dateTrunc": {"date": {"$toDate": "$date"}, "unit": "day"}},
            "count": {"$count": {}}
        }

    @staticmethod
    def _set() -> dict:
        return {"day": "$_id"}
