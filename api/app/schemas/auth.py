from pydantic import BaseModel, EmailStr
from app.models.business import BusinessType


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""

    user_id: int | None = None


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str
    name: str
    phone: str | None = None


class BusinessAdminLogin(BaseModel):
    """Business admin login schema."""

    email: EmailStr
    password: str


class BusinessAdminRegister(BaseModel):
    """Business admin registration with business creation."""

    # Admin data
    email: EmailStr
    password: str

    # Business data
    business_name: str
    business_type: BusinessType
    address: str
    lat: float
    lon: float
    phone: str
    business_email: str | None = None
    description: str | None = None
