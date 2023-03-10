from datetime import datetime

from pydantic import Field
from db_handler import PyObjectId, SchemaMetaclass

from ..database import models
from ._base import PaginatedModel


class _PyObjectIdSchema(PyObjectId):
    """Needed for API docs to properly display the schema"""

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ReportOut(models.Report, metaclass=SchemaMetaclass):
    """Schema for individual reports"""

    id: _PyObjectIdSchema = Field(..., description="Unique identifier in DB", alias="_id")
    date: datetime = Field(..., description="Date and time of creation (UTC)")

    class Config:
        json_encoders = {PyObjectId: str}


class ReportIn(ReportOut):
    """Schema for report insertion"""

    __exclude__ = {"id", "date"}


class ReportUpdate(ReportIn):
    """Schema for report updating"""

    __all_optional__ = True


class PaginatedReports(PaginatedModel):
    """Schema for paginated reports"""

    results: list[ReportOut] = Field(..., description="List of reports matching query")

    class Config(ReportOut.Config):
        """This class is necessary to parse ObjectID fields nested in results"""
