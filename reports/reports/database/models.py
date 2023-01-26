from datetime import datetime, timezone

from pymongo import IndexModel
from pydantic import BaseModel, Field
from db_handler import PyObjectId, ModelMetaclass


def _oid() -> PyObjectId:
    return PyObjectId()


def _utcnow() -> datetime:
    now = datetime.now(timezone.utc)
    # Needed to keep in line with format allowed in MongoDB (millisecond resolution, unmarked TZ)
    return now.replace(microsecond=(now.microsecond // 1000) * 1000, tzinfo=None)


class Report(BaseModel, metaclass=ModelMetaclass):
    """Full mongo model for reports"""

    __tablename__ = "reports"
    __indexes__ = [IndexModel([("owner", 1), ("object", 1), ("report_type", 1)], unique=True), IndexModel([("date", -1)])]

    id: PyObjectId = Field(default_factory=_oid, description="Unique identifier in DB", alias="_id")
    date: datetime = Field(default_factory=_utcnow, description="Date and time of creation (UTC)")
    object: str = Field(..., description="Reported object ID")
    solved: bool = Field(..., description="Report status")
    source: str = Field(..., description="Service of origin of the report")
    observation: str = Field(..., description="Commentary on the report")
    report_type: str = Field(..., description="Type of report")
    owner: str = Field(..., description="User who created the report")
