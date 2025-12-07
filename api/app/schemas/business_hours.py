"""Business hours schemas."""
from datetime import time
from pydantic import BaseModel, Field


class BusinessHoursBase(BaseModel):
    """Base business hours schema."""

    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    open_time: time | None = Field(None, description="Opening time")
    close_time: time | None = Field(None, description="Closing time")
    is_closed: bool = Field(False, description="Whether business is closed on this day")


class BusinessHoursCreate(BusinessHoursBase):
    """Schema for creating business hours."""

    pass


class BusinessHoursUpdate(BaseModel):
    """Schema for updating business hours."""

    open_time: time | None = None
    close_time: time | None = None
    is_closed: bool | None = None


class BusinessHoursResponse(BusinessHoursBase):
    """Schema for business hours response."""

    id: int
    business_id: int

    class Config:
        from_attributes = True


class BusinessHoursBulkUpdate(BaseModel):
    """Schema for bulk updating all business hours (all 7 days)."""

    hours: list[BusinessHoursCreate] = Field(
        ..., min_length=7, max_length=7, description="Hours for all 7 days of the week"
    )
