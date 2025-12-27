from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import Gender


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr | None = None
    name: str
    phone: str | None = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserProfileUpdate(BaseModel):
    """User profile update schema (for client settings)."""

    name: str | None = None
    gender: Gender | None = None
    email: EmailStr | None = None
    # phone is read-only (used for OTP login)


class User(BaseModel):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None = None
    phone: str | None = None
    name: str
    gender: Gender | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime
