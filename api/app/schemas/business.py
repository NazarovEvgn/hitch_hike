from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BusinessBase(BaseModel):
    """Base business schema."""

    name: str
    type: str
    address: str
    lat: float
    lon: float
    phone: str
    email: str | None = None
    description: str | None = None


class BusinessCreate(BusinessBase):
    """Business creation schema."""

    pass


class BusinessUpdate(BaseModel):
    """Business update schema."""

    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    logo_url: str | None = None


class BusinessStatusUpdate(BaseModel):
    """Business status update schema."""

    status: str  # available, busy
    estimated_wait_minutes: int = 0


class Business(BusinessBase):
    """Business response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    logo_url: str | None = None
    dgis_id: str | None = None
    subscription_status: str
    subscription_end_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
