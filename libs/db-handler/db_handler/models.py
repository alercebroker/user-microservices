from datetime import datetime

from pymongo import IndexModel
from pydantic import Field

from .utils import BaseModelWithId, now_utc


class Report(BaseModelWithId):
    """Schema for individual reports"""
    __tablename__ = "reports"
    __indexes__ = [
        IndexModel([("owner", 1), ("object", 1), ("report_type", 1)], unique=True),
        IndexModel([("date", -1)])
    ]

    date: datetime = Field(default_factory=now_utc, description="Date the report was generated")
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Whether the report has been solved")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="Report owner")
