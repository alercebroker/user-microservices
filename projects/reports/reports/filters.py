from datetime import datetime
from typing import Literal, Pattern, NamedTuple, ClassVar

from fastapi import Query
from pydantic.dataclasses import dataclass

from .models import Report, ByObjectReport, ByDayReport


class _QueryRecipe(NamedTuple):
    field: str
    operators: list[str]
    attributes: list[str]


@dataclass
class _BaseQuery:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    page: int = Query(1, description="Page for paginated results")
    page_size: int = Query(10, description="Number of reports per page")
    order_by: Literal[""] = Query("", description="NEEDS TO BE OVERRIDEN!!")
    direction: Literal["1", "-1"] = Query(-1, description="Sort by ascending or descending values")

    _recipes: ClassVar[tuple[_QueryRecipe]] = (
        _QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        _QueryRecipe("object", ["$regex"], ["object"])
    )

    def _match(self) -> dict:
        def query(ops, attrs):
            return {op: getattr(self, attr) for op, attr in zip(ops, attrs) if getattr(self, attr) is not None}

        query = {field: query(ops, attrs) for field, ops, attrs in self._recipes}
        return {"$match": {k: v for k, v in query.items() if v}}

    def _sort(self) -> dict:
        return {"$sort": {self.order_by: int(self.direction)}}

    def _skip(self) -> dict:
        return {"$skip": (self.page - 1) * self.page_size}

    def _limit(self) -> dict:
        return {"$limit": self.page_size}

    def pipeline(self) -> list[dict]:
        return [self._match(), self._sort(), self._skip(), self._limit()]


@dataclass
class QueryByReport(_BaseQuery):
    order_by: Literal[tuple(Report.__fields__)] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(_BaseQuery):
    order_by: Literal[tuple(ByObjectReport.__fields__)] = Query("last_date", description="Field to sort by")

    @staticmethod
    def _group() -> dict:
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

    def pipeline(self) -> list[dict]:
        return [self._match(), self._group(), self._sort(), self._skip(), self._limit()]


@dataclass
class QueryByDay(_BaseQuery):
    order_by: Literal[tuple(ByDayReport.__fields__)] = Query("day", description="Field to sort by")

    @staticmethod
    def _group() -> dict:
        return {
            "$group": {
                "_id": {"$dateTrunc": {"date": {"$toDate": "$date"}, "unit": "day"}},
                "count": {"$count": {}}
            }
        }

    def pipeline(self) -> list[dict]:
        return [self._match(), self._group(), self._sort(), self._skip(), self._limit()]
