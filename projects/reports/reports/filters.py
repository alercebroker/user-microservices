from datetime import datetime
from typing import Literal, Pattern
from pydantic.dataclasses import dataclass

from fastapi import Query

from .models import Report, ReportByObject


@dataclass
class BaseQuery:
    date_after: datetime | None = Query(None, description="Starting date of reports")
    date_before: datetime | None = Query(None, description="End date of reports")
    object: str | None = Query(None, description="Reports for this object ID")
    object_contains: Pattern | None = Query(None, description="Reports for object IDs matching regex")
    owned: bool = Query(False, description="Whether to include only reports owned by requesting user")
    page: int = Query(1, description="Page for paginated results")
    page_size: int = Query(10, description="Number of reports per page")
    order_mode: Literal["ASC", "DESC"] = Query("DESC", description="Sort by ascending or descending values")


@dataclass
class QueryByReport(BaseQuery):
    order_by: Literal[tuple(Report.__fields__)] = Query("date", description="Field to sort by")


@dataclass
class QueryByObject(BaseQuery):
    order_by: Literal[tuple(ReportByObject.__fields__)] = Query("last_date", description="Field to sort by")
