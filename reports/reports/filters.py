from datetime import datetime
from typing import Pattern, ClassVar

import query
from fastapi import Query
from pydantic import dataclasses

from .schemas import ReportOut, ReportByObject, ReportByDay


ReportFields = query.field_enum_factory(ReportOut)
ObjectFields = query.field_enum_factory(ReportByObject)
DayCountFields = query.field_enum_factory(ReportByDay)


@dataclasses.dataclass
class CommonQueries:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")

    recipes: ClassVar[tuple[query.QueryRecipe]] = (
        query.QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        query.QueryRecipe("object", ["$regex"], ["object"]),
    )


@dataclasses.dataclass
class QueryByReport(CommonQueries, query.BasePaginatedQuery):
    """Queries that will return individual reports, directly as they come from the database."""

    order_by: ReportFields = Query(ReportFields.date, description="Field to sort by")


@dataclasses.dataclass
class QueryByObject(CommonQueries, query.BasePaginatedQuery):
    """Queries that will return reports grouped by object."""

    order_by: ObjectFields = Query(ObjectFields.last_date, description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {
            "_id": "$object",
            "first_date": {"$min": "$date"},
            "last_date": {"$max": "$date"},
            "users": {"$addToSet": "$owner"},
            "source": {"$addToSet": "$source"},
            "report_type": {"$addToSet": "$report_type"},
            "count": {"$count": {}},
        }
        return super()._query_pipeline() + [{"$group": group}, {"$set": {"object": "$_id"}}]


@dataclasses.dataclass
class QueryByDay(CommonQueries, query.BaseSortedQuery):
    """Queries that return number of reports per day."""

    order_by: DayCountFields = Query(DayCountFields.day, description="Field to sort by")

    def _query_pipeline(self) -> list[dict]:
        group = {"_id": {"$dateTrunc": {"date": "$date", "unit": "day"}}, "count": {"$count": {}}}
        return super()._query_pipeline() + [{"$group": group}, {"$set": {"day": "$_id"}}]
