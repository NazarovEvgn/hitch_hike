from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BusinessPhotoBase(BaseModel):
    """Base business photo schema."""

    photo_url: str
    display_order: int = 0


class BusinessPhotoCreate(BusinessPhotoBase):
    """Business photo creation schema."""

    pass


class BusinessPhotoUpdate(BaseModel):
    """Business photo update schema."""

    photo_url: str | None = None
    is_main: bool | None = None
    display_order: int | None = None


class BusinessPhoto(BusinessPhotoBase):
    """Business photo response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    is_main: bool
    created_at: datetime
