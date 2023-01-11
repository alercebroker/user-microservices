from datetime import datetime
from typing import Literal, Pattern, NamedTuple, ClassVar

from fastapi import Query
from pydantic.dataclasses import dataclass

from .models import Report, ReportByObject, ReportByDay


class _QueryRecipe(NamedTuple):
    field: str
    operators: list[str]
    attributes: list[str]


@dataclass
class BaseQuery:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    page: int = Query(1, description="Page for paginated results", ge=1)
    page_size: int = Query(10, description="Number of reports per page", ge=1)
    order_by: Literal[""] = Query("", description="NEEDS TO BE OVERRIDEN!!")
    direction: Literal["1", "-1"] = Query(-1, description="Sort by ascending or descending values")

    _recipes: ClassVar[tuple[_QueryRecipe]] = (
        _QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        _QueryRecipe("object", ["$regex"], ["object"])
    )

    def query(self) -> dict:
        def query(ops, attrs):
            return {op: getattr(self, attr) for op, attr in zip(ops, attrs) if getattr(self, attr) is not None}

        query = {field: query(ops, attrs) for field, ops, attrs in self._recipes}
        return {k: v for k, v in query.items() if v}

    def sort(self) -> dict:
        return {self.order_by: int(self.direction)}

    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    def limit(self) -> int:
        return self.page_size

    def _base_pipeline(self) -> list[dict]:
        return [{"$match": self.query()}]

    def _base_pagination(self) -> list[dict]:
        return [{"$sort": self.sort()}, {"$skip": self.skip()}, {"$limit": self.limit()}]

    def pipeline(self, paginate=True, count=False) -> list[dict]:
        pipeline = self._base_pipeline()
        pipeline = pipeline + self._base_pagination() if paginate else pipeline
        pipeline = pipeline + [{"$count": "total"}] if count else pipeline
        return pipeline


@dataclass
class QueryByReport(BaseQuery):
    order_by: Literal[tuple(Report.__fields__)] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(BaseQuery):
    order_by: Literal[tuple(ReportByObject.__fields__)] = Query("last_date", description="Field to sort by")

    @staticmethod
    def group() -> dict:
        return {
            "$group": {
                "_id": "$object",
                "first_date": {"$min": "$date"},
                "last_date": {"$max": "$date"},
                "users": {"$addToSet": "$owner"},
                "source": {"$addToSet": "$source"},
                "report_type": {"$addToSet": "$report_type"},
                "count": {"$count": {}}
            }
        }

    @staticmethod
    def set() -> dict:
        return {"$set": {"object": "$_id"}}

    def _base_pipeline(self) -> list[dict]:
        return [{"$match": self.query()}, self.group(), self.set()]


@dataclass
class QueryByDay(QueryByObject):
    order_by: Literal[tuple(ReportByDay.__fields__)] = Query("day", description="Field to sort by")

    @staticmethod
    def group() -> dict:
        return {
            "$group": {
                "_id": {"$dateTrunc": {"date": {"$toDate": "$date"}, "unit": "day"}},
                "count": {"$count": {}}
            }
        }

    @staticmethod
    def set() -> dict:
        return {"$set": {"day": "$_id"}}
