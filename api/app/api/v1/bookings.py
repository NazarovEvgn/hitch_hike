from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.business import Business
from app.models.service import Service
from app.schemas.booking import Booking as BookingSchema, BookingCreate

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(lambda: None),  # Optional auth
):
    """
    Create a new booking.

    Can be created by authenticated user or guest (no auth required for MVP).
    """
    # Verify business exists
    business_result = await db.execute(
        select(Business).where(Business.id == booking_data.business_id)
    )
    business = business_result.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    # Verify service exists and belongs to business
    service_result = await db.execute(
        select(Service).where(
            and_(
                Service.id == booking_data.service_id,
                Service.business_id == booking_data.business_id,
                Service.is_active == True,
            )
        )
    )
    service = service_result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found or inactive",
        )

    # Create booking
    new_booking = Booking(
        business_id=booking_data.business_id,
        user_id=current_user.id if current_user else None,
        service_id=booking_data.service_id,
        booking_date=booking_data.booking_date,
        booking_time=booking_data.booking_time,
        client_name=booking_data.client_name,
        client_phone=booking_data.client_phone,
        notes=booking_data.notes,
        status=BookingStatus.PENDING,
    )

    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    return new_booking


@router.get("/my", response_model=list[BookingSchema])
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all bookings for the authenticated user."""
    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.booking_date.desc(), Booking.booking_time.desc())
    )
    bookings = result.scalars().all()
    return bookings


@router.get("/{booking_id}", response_model=BookingSchema)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific booking."""
    result = await db.execute(
        select(Booking).where(
            and_(Booking.id == booking_id, Booking.user_id == current_user.id)
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingSchema)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a booking."""
    result = await db.execute(
        select(Booking).where(
            and_(Booking.id == booking_id, Booking.user_id == current_user.id)
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking already cancelled",
        )

    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed booking",
        )

    booking.status = BookingStatus.CANCELLED
    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    return booking
