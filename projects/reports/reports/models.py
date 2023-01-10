from datetime import datetime

from db_handler.models import BaseModelWithId
from pydantic import BaseModel, Field


class Report(BaseModelWithId):
    date: datetime = Field(default_factory=datetime.now, description="Date the report was generated")
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")


class ReportIn(BaseModel):
    object: str | None = Field(None, description="Reported object ID")
    solved: bool | None = Field(None, description="Whether the report has been solved")
    source: str | None = Field(None, description="Service of origin of the report")
    observation: str | None = Field(None, description="Class assigned to the object")
    report_type: str | None = Field(None, description="Type of report")
    owner: str | None = Field(None, description="Report owner")
