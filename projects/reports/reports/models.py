from datetime import date, datetime

from db_handler.models import Report
from pydantic import BaseModel, Field


class InsertReport(BaseModel):
    """Schema for report creation"""
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")


class PaginatedModel(BaseModel):
    """Basic schema for paginated results"""
    count: int = Field(..., description="Total number of results matching query")
    next: int | None = Field(..., description="Next page number (null if no next page)")
    previous: int | None = Field(..., description="Previous page number (null if no previous page)")


class PaginatedReports(PaginatedModel):
    """Schema for paginated reports"""
    results: list[Report] = Field(..., description="List of reports matching query")

    class Config(Report.Config):
        """This class is necessary to parse ObjectID fields nested in results"""


class ReportByObject(BaseModel):
    """Schema for reports grouped by object"""
    object: str = Field(..., description="Reported object ID")
    first_date: datetime = Field(..., description="Date of first report")
    last_date: datetime = Field(..., description="Date of last report")
    count: int = Field(..., description="Number of reports")
    source: list[str] = Field(..., description="Service(s) of origin of the reports")
    report_type: list[str] = Field(..., description="Type(s) of reports")
    users: list[str] = Field(..., description="Reporting user(s)")


class PaginatedReportsByObject(PaginatedModel):
    """Schema for paginated reports grouped by object"""
    results: list[ReportByObject] = Field(..., description="List of objects matching query")


class ReportByDay(BaseModel):
    """Schema for number of reports per day"""
    day: date = Field(..., description="Day with aggregate reports")
    count: int = Field(..., description="Number of reports in the day")
