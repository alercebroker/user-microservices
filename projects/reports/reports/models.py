from datetime import date, datetime, timezone

from db_handler.models import BaseModelWithId
from pydantic import BaseModel, Field


def now_utc():
    return datetime.now(timezone.utc)


class Report(BaseModelWithId):
    date: datetime = Field(default_factory=now_utc, description="Date the report was generated")
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")


class InsertReport(BaseModel):
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")


class UpdateReport(BaseModel):
    object: str | None = Field(None, description="Reported object ID")
    solved: bool | None = Field(None, description="Whether the report has been solved")
    source: str | None = Field(None, description="Service of origin of the report")
    observation: str | None = Field(None, description="Class assigned to the object")
    report_type: str | None = Field(None, description="Type of report")
    owner: str | None = Field(None, description="Report owner")


class ByObjectReport(BaseModel):
    object: str = Field(..., description="Reported object ID")
    first_date: datetime = Field(..., description="Date of first report")
    last_date: datetime = Field(..., description="Date of last report")
    count: int = Field(..., description="Number of reports")
    source: list[str] = Field(..., description="Service(s) of origin of the reports")
    report_type: list[str] = Field(..., description="Type(s) of reports")
    users: list[str] = Field(..., description="Reporting user(s)")


class ByDayReport(BaseModel):
    day: date = Field(..., description="Day with aggregate reports")
    count: int = Field(..., description="Number of reports in the day")
