from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    """Base booking schema."""

    service_id: int
    employee_id: int | None = None
    booking_date: date
    booking_time: time
    client_name: str
    client_phone: str
    notes: str | None = None


class BookingCreate(BookingBase):
    """Booking creation schema for admin."""

    pass


class BookingUpdate(BaseModel):
    """Booking update schema."""

    status: str  # pending, confirmed, completed, cancelled
    came_through_app: bool | None = None


class Booking(BookingBase):
    """Booking response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    user_id: int | None = None
    employee_id: int | None = None
    status: str
    came_through_app: bool
    created_at: datetime
    updated_at: datetime
