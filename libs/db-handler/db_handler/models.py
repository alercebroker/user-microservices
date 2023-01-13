from datetime import datetime

from pymongo import IndexModel
from pydantic import Field

from .utils import BaseModelWithId


class Report(BaseModelWithId):
    """Full mongo model for reports"""
    __tablename__ = "reports"
    __indexes__ = [
        IndexModel([("owner", 1), ("object", 1), ("report_type", 1)], unique=True),
        IndexModel([("date", -1)])
    ]

    date: datetime = Field(default_factory=datetime.utcnow, description="Date and time of creation (UTC)")
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Report status")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Class assigned to the object")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="User who created the report")
