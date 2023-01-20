from datetime import date

from pydantic import BaseModel, Field


class ReportByDay(BaseModel):
    """Schema for number of reports per day"""
    day: date = Field(..., description="Day (start and end at UTC)")
    count: int = Field(..., description="Number of reports in the day")
