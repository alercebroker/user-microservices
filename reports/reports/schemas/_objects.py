from datetime import datetime

from pydantic import BaseModel, Field

from ._base import PaginatedModel


class ReportByObject(BaseModel):
    """Schema for reports grouped by object"""

    object: str = Field(..., description="Reported object ID")
    first_date: datetime = Field(..., description="Date and time of first report (UTC)")
    last_date: datetime = Field(..., description="Date and time of last report (UTC)")
    count: int = Field(..., description="Number of reports")
    report_type: str = Field(..., description="Type of report")
    users: list[str] = Field(..., description="Reporting user(s) IDs")


class PaginatedReportsByObject(PaginatedModel):
    """Schema for paginated reports grouped by object"""

    results: list[ReportByObject] = Field(..., description="List of objects matching query")
