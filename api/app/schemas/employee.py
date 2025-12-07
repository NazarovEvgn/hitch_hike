from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    """Base employee schema."""

    name: str
    phone: str | None = None
    position: str | None = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    """Employee creation schema."""

    pass


class EmployeeUpdate(BaseModel):
    """Employee update schema."""

    name: str | None = None
    phone: str | None = None
    position: str | None = None
    is_active: bool | None = None


class Employee(EmployeeBase):
    """Employee response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    created_at: datetime
    updated_at: datetime
