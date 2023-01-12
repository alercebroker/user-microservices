from datetime import date, datetime, timezone
from typing import ClassVar

from db_handler.models import BaseModelWithId
from pydantic import BaseModel as PydanticBaseModel, Field


def now_utc():
    return datetime.now(timezone.utc)


class BaseModel(PydanticBaseModel):
    @classmethod
    def get_fields(cls, alias: bool = True) -> tuple:
        return tuple(cls.schema(alias).get("properties"))


class InsertReport(BaseModel):
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")


class Report(InsertReport, BaseModelWithId):
    __tablename__: ClassVar[str] = "reports"

    date: datetime = Field(default_factory=now_utc, description="Date the report was generated")


class PaginatedModel(BaseModel):
    count: int = Field(..., description="Total number of results matching query")
    next: int | None = Field(..., description="Next page number (null if no next page)")
    previous: int | None = Field(..., description="Previous page number (null if no previous page)")


class PaginatedReports(PaginatedModel):
    results: list[Report] = Field(..., description="List of reports matching query")

    class Config(BaseModelWithId.Config):
        """This class is necessary to parse ObjectID fields nested in results"""


class ReportByObject(BaseModel):
    object: str = Field(..., description="Reported object ID")
    first_date: datetime = Field(..., description="Date of first report")
    last_date: datetime = Field(..., description="Date of last report")
    count: int = Field(..., description="Number of reports")
    source: list[str] = Field(..., description="Service(s) of origin of the reports")
    report_type: list[str] = Field(..., description="Type(s) of reports")
    users: list[str] = Field(..., description="Reporting user(s)")


class PaginatedReportsByObject(PaginatedModel):
    results: list[ReportByObject] = Field(..., description="List of objects matching query")


class ReportByDay(BaseModel):
    day: date = Field(..., description="Day with aggregate reports")
    count: int = Field(..., description="Number of reports in the day")


class PaginatedReportsByDay(PaginatedModel):
    results: list[ReportByDay] = Field(..., description="List of days matching query")
