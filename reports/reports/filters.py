from datetime import datetime
from typing import Pattern, ClassVar, Literal

import query
from fastapi import Query
from pydantic import dataclasses

from .schemas import ReportOut, ReportByObject, ReportByDay


reports_fields = query.fields(ReportOut)
objects_fields = query.fields(ReportByObject, exclude={"users"})
day_fields = query.fields(ReportByDay)


@dataclasses.dataclass
class CommonQueries:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    type: Literal["TOM", "Bogus"] | None = Query(None, description="Report type")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")

    recipes: ClassVar[tuple[query.QueryRecipe]] = (
        query.QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        query.QueryRecipe("object", ["$regex"], ["object"]),
        query.QueryRecipe("report_type", ["$eq"], ["type"]),
    )

    @staticmethod
    def _rename_id(fields, key):
        project = {k: True for k in fields if k != "_id"}
        project[key] = "$_id"
        project["_id"] = False
        return project


@dataclasses.dataclass
class QueryByReport(CommonQueries, query.BasePaginatedQuery):
    """Queries that will return individual reports, directly as they come from the database."""

    order_by: Literal[reports_fields] = Query("date", description="Field to sort by")


@dataclasses.dataclass
class QueryByObject(CommonQueries, query.BasePaginatedQuery):
    """Queries that will return reports grouped by object."""

    order_by: Literal[objects_fields] = Query("last_date", description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {
            "_id": "$object",
            "first_date": {"$min": "$date"},
            "last_date": {"$max": "$date"},
            "users": {"$addToSet": "$owner"},
            "count": {"$count": {}},
        }
        return super()._query_pipeline() + [{"$group": group}, {"$project": self._rename_id(group, "object")}]


@dataclasses.dataclass
class QueryByDay(CommonQueries, query.BaseSortedQuery):
    """Queries that return number of reports per day."""

    order_by: Literal[day_fields] = Query("day", description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {"_id": {"$dateTrunc": {"date": "$date", "unit": "day"}}, "count": {"$count": {}}}
        return super()._query_pipeline() + [{"$group": group}, {"$project": self._rename_id(group, "day")}]
