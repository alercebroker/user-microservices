from datetime import datetime
from typing import Literal, Pattern, NamedTuple, ClassVar

from fastapi import Query
from pydantic.dataclasses import dataclass

from .models import Report, ReportByObject, ReportByDay


class QueryRecipe(NamedTuple):
    field: str
    operators: list[str]
    attributes: list[str]

    def pair(self, q) -> tuple[str, dict]:
        values = (getattr(q, attr) for attr in self.attributes)
        condition = {op: val for op, val in zip(self.operators, values) if val is not None}
        return self.field, condition


@dataclass
class BaseQuery:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    page: int = Query(1, description="Page for paginated results", ge=1)
    page_size: int = Query(10, description="Number of reports per page", ge=1)
    order_by: Literal[""] = Query("", description="NEEDS TO BE OVERRIDEN!!")
    direction: Literal["1", "-1"] = Query("-1", description="Sort by ascending or descending values")

    _recipes: ClassVar[tuple[QueryRecipe]] = (
        QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        QueryRecipe("object", ["$regex"], ["object"])
    )

    def __query(self) -> dict:
        return {k: v for k, v in (r.pair(self) for r in self._recipes) if v}

    def __sort(self) -> dict | None:
        return {self.order_by: int(self.direction)} if self.order_by else None

    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    def limit(self) -> int:
        return self.page_size

    def _filter(self) -> list[dict]:
        return [{"$match": self.__query()}]

    def __page(self) -> list[dict]:
        sort = [{"$sort": self.__sort()}] if self.__sort() else []
        return sort + [{"$skip": self.skip()}, {"$limit": self.limit()}]

    def pipeline(self, paginate: bool = True, count: bool = False) -> list[dict]:
        paginate = self.__page() if paginate else []
        count = [{"$count": "total"}] if count else []
        return self._filter() + paginate + count


@dataclass
class QueryByReport(BaseQuery):
    order_by: Literal[Report.get_fields()] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(BaseQuery):
    order_by: Literal[ReportByObject.get_fields()] = Query("last_date", description="Field to sort by")

    @staticmethod
    def _group() -> dict:
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
        return {"object": "$_id"}

    def _filter(self) -> list[dict]:
        return [{"$match": self.__query()}, {"$group": self._group()}, {"$set": self._set()}]


@dataclass
class QueryByDay(QueryByObject):
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
