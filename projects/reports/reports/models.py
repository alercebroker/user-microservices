from datetime import date, datetime

from db_handler.models import Report as ReportDB
from db_handler.utils import SchemaMetaclass
from pydantic import BaseModel, Field


class Report(ReportDB, metaclass=SchemaMetaclass):
    """Schema for individual reports"""


class ReportInsert(Report):
    """Schema for report insertion"""
    __exclude__ = {"id", "date"}


class ReportUpdate(ReportInsert):
    """Schema for report updating"""
    __all_optional__ = True


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
