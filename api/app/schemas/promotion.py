from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PromotionBase(BaseModel):
    """Base promotion schema."""

    title: str
    description: str
    discount_percent: int | None = None
    valid_from: datetime
    valid_until: datetime


class PromotionCreate(PromotionBase):
    """Promotion creation schema."""

    pass


class PromotionUpdate(BaseModel):
    """Promotion update schema."""

    title: str | None = None
    description: str | None = None
    discount_percent: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None


class Promotion(PromotionBase):
    """Promotion response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    is_active: bool
    created_at: datetime
