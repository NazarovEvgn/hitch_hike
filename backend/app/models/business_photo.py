from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BusinessPhoto(Base):
    """Business photo model for gallery."""

    __tablename__ = "business_photos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    photo_url: Mapped[str] = mapped_column(String(500))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    business: Mapped["Business"] = relationship("Business", back_populates="photos")
