from datetime import datetime, time
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum, Time, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON
import enum

from app.core.database import Base


class BusinessType(str, enum.Enum):
    """Business type enumeration."""

    CAR_WASH = "car_wash"
    REPAIR_SHOP = "repair_shop"
    TIRE_SERVICE = "tire_service"
    BEAUTY_SALON = "beauty_salon"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration."""

    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AvailabilityStatus(str, enum.Enum):
    """Business availability status."""

    AVAILABLE = "available"  # Свободны. Готовы принять сразу
    BUSY = "busy"  # Работаем (примерное время ожидания указывается отдельно)


class Business(Base):
    """Auto service business model."""

    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[BusinessType] = mapped_column(
        SQLEnum(BusinessType, values_callable=lambda x: [e.value for e in x])
    )
    address: Mapped[str] = mapped_column(String(500))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    phones: Mapped[list[str]] = mapped_column(JSON, default=list, server_default='[]')
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dgis_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus, values_callable=lambda x: [e.value for e in x]),
        default=SubscriptionStatus.TRIAL,
    )
    subscription_end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    admins: Mapped[list["BusinessAdmin"]] = relationship(
        "BusinessAdmin", back_populates="business", lazy="selectin"
    )
    services: Mapped[list["Service"]] = relationship(
        "Service", back_populates="business", lazy="selectin"
    )
    current_status: Mapped["BusinessStatus"] = relationship(
        "BusinessStatus", back_populates="business", uselist=False, lazy="selectin"
    )
    status_history: Mapped[list["StatusHistory"]] = relationship(
        "StatusHistory", back_populates="business", lazy="selectin"
    )
    business_hours: Mapped[list["BusinessHours"]] = relationship(
        "BusinessHours", back_populates="business", lazy="selectin"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="business", lazy="selectin"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="business", lazy="selectin"
    )
    promotions: Mapped[list["Promotion"]] = relationship(
        "Promotion", back_populates="business", lazy="selectin"
    )
    photos: Mapped[list["BusinessPhoto"]] = relationship(
        "BusinessPhoto", back_populates="business", lazy="selectin"
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="business", lazy="selectin"
    )


class BusinessAdmin(Base):
    """Business administrator model."""

    __tablename__ = "business_admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="admins")


class BusinessStatus(Base):
    """Current business availability status."""

    __tablename__ = "business_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"), unique=True, index=True
    )
    status: Mapped[AvailabilityStatus] = mapped_column(
        SQLEnum(AvailabilityStatus, values_callable=lambda x: [e.value for e in x]),
        default=AvailabilityStatus.AVAILABLE,
    )
    estimated_wait_minutes: Mapped[int] = mapped_column(Integer, default=0)
    updated_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("business_admins.id"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="current_status")


class StatusHistory(Base):
    """Historical record of status changes for analytics."""

    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    status: Mapped[AvailabilityStatus] = mapped_column(
        SQLEnum(AvailabilityStatus, values_callable=lambda x: [e.value for e in x])
    )
    estimated_wait_minutes: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="status_history")


class BusinessHours(Base):
    """Business working hours for each day of the week."""

    __tablename__ = "business_hours"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0=Monday, 6=Sunday
    open_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    close_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="business_hours")
