from pydantic import BaseModel, Field


class PaginatedModel(BaseModel):
    """Basic schema for paginated results"""
    count: int = Field(..., description="Total number of results matching query")
    next: int | None = Field(..., description="Next page number (null if no next page)")
    previous: int | None = Field(..., description="Previous page number (null if no previous page)")
