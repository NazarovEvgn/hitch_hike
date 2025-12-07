"""Available time slots schemas."""
import datetime
from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    """Single time slot."""

    time: str = Field(..., description="Time in HH:MM format")
    available: bool = Field(..., description="Whether this slot is available for booking")


class AvailableSlotsRequest(BaseModel):
    """Request for available slots."""

    business_id: int = Field(..., description="Business ID")
    service_id: int = Field(..., description="Service ID (for duration)")
    date: datetime.date = Field(..., description="Date to check availability")


class AvailableSlotsResponse(BaseModel):
    """Response with available slots."""

    date: datetime.date
    slots: list[TimeSlot]
    business_hours: dict[str, str | None] = Field(
        ..., description="Opening hours for the day (open_time, close_time)"
    )
