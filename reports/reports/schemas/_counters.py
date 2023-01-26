from datetime import date

from pydantic import BaseModel, Field


class ReportByDay(BaseModel):
    """Schema for number of reports per day"""

    day: date = Field(..., description="Day (UTC)")
    count: int = Field(..., description="Number of reports in the day")


class ReportByUser(BaseModel):
    """Schema for number of reports per day"""

    user: str = Field(..., description="User name")
    count: int = Field(..., description="Number of reports by user")
