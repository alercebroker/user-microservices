from datetime import datetime
from typing import Pattern, ClassVar

from fastapi import Query
from pydantic.dataclasses import dataclass
from query import QueryRecipe, BaseSortedQuery, BasePaginatedQuery, field_enum_factory

from .models import ReportOut, ReportByObject, ReportByDay


ReportFields = field_enum_factory(ReportOut)
ObjectFields = field_enum_factory(ReportByObject)
DayCountFields = field_enum_factory(ReportByDay)


@dataclass
class QueryByReport(BasePaginatedQuery):
    """Queries that will return individual reports, directly as they come from the database."""
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    order_by: ReportFields = Query("date", description="Field to sort by")

    recipes: ClassVar[tuple[QueryRecipe]] = (
        QueryRecipe("date", ["$gte", "$lte"], ["date_after", "date_before"]),
        QueryRecipe("object", ["$regex"], ["object"])
    )


@dataclass
class QueryByObject(QueryByReport):
    """Queries that will return reports grouped by object."""
    order_by: ObjectFields = Query("last_date", description="Field to sort by")

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
class QueryByDay(BaseSortedQuery):
    """Queries that return number of reports per day."""
    order_by: DayCountFields = Query("day", description="Field to sort by")

    recipes: ClassVar[tuple[QueryRecipe]] = ()

    def _query_pipeline(self) -> list[dict]:
        group = {
            "_id": {
                "$dateTrunc": {
                    "date": "$date",
                    "unit": "day"
                }
            },
            "count": {"$count": {}}
        }
        return super()._query_pipeline() + [{"$group": group}, {"$set": {"day": "$_id"}}]
