from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete

from app.core.database import get_db
from app.api.dependencies import get_current_business_admin
from app.models.business import Business, BusinessAdmin, BusinessStatus, StatusHistory, AvailabilityStatus, BusinessHours
from app.models.service import Service
from app.models.booking import Booking, BookingStatus
from app.models.promotion import Promotion
from app.schemas.business import Business as BusinessSchema, BusinessUpdate, BusinessStatusUpdate
from app.schemas.service import Service as ServiceSchema, ServiceCreate, ServiceUpdate
from app.schemas.booking import Booking as BookingSchema, BookingUpdate
from app.schemas.promotion import Promotion as PromotionSchema, PromotionCreate, PromotionUpdate
from app.schemas.business_hours import BusinessHoursResponse, BusinessHoursBulkUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# BUSINESS PROFILE MANAGEMENT
# =============================================================================

@router.get("/business/profile", response_model=BusinessSchema)
async def get_business_profile(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get business profile for current admin."""
    result = await db.execute(
        select(Business).where(Business.id == current_admin.business_id)
    )
    business = result.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.patch("/business/profile", response_model=BusinessSchema)
async def update_business_profile(
    business_data: BusinessUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update business profile."""
    result = await db.execute(
        select(Business).where(Business.id == current_admin.business_id)
    )
    business = result.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    # Update only provided fields
    update_data = business_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)

    business.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(business)

    return business


# =============================================================================
# STATUS MANAGEMENT
# =============================================================================

@router.patch("/status")
async def update_business_status(
    status_data: BusinessStatusUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update business availability status."""
    # Get or create business status
    result = await db.execute(
        select(BusinessStatus).where(BusinessStatus.business_id == current_admin.business_id)
    )
    business_status = result.scalar_one_or_none()

    if business_status:
        # Update existing status
        business_status.status = AvailabilityStatus(status_data.status)
        business_status.estimated_wait_minutes = status_data.estimated_wait_minutes
        business_status.updated_by_admin_id = current_admin.id
        business_status.updated_at = datetime.utcnow()
    else:
        # Create new status
        business_status = BusinessStatus(
            business_id=current_admin.business_id,
            status=AvailabilityStatus(status_data.status),
            estimated_wait_minutes=status_data.estimated_wait_minutes,
            updated_by_admin_id=current_admin.id,
        )
        db.add(business_status)

    # Add to history
    status_history = StatusHistory(
        business_id=current_admin.business_id,
        status=AvailabilityStatus(status_data.status),
        estimated_wait_minutes=status_data.estimated_wait_minutes,
    )
    db.add(status_history)

    await db.commit()

    return {
        "success": True,
        "status": business_status.status.value,
        "estimated_wait_minutes": business_status.estimated_wait_minutes,
        "updated_at": business_status.updated_at,
    }


@router.get("/status/current")
async def get_current_status(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get current business status."""
    result = await db.execute(
        select(BusinessStatus).where(BusinessStatus.business_id == current_admin.business_id)
    )
    business_status = result.scalar_one_or_none()

    if not business_status:
        return {
            "status": "available",
            "estimated_wait_minutes": 0,
            "updated_at": None,
        }

    return {
        "status": business_status.status.value,
        "estimated_wait_minutes": business_status.estimated_wait_minutes,
        "updated_at": business_status.updated_at,
    }


@router.get("/status/history")
async def get_status_history(
    limit: int = 50,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get status update history."""
    result = await db.execute(
        select(StatusHistory)
        .where(StatusHistory.business_id == current_admin.business_id)
        .order_by(StatusHistory.updated_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()

    return [
        {
            "status": h.status.value,
            "estimated_wait_minutes": h.estimated_wait_minutes,
            "updated_at": h.updated_at,
        }
        for h in history
    ]


# =============================================================================
# SERVICES MANAGEMENT
# =============================================================================

@router.get("/services", response_model=list[ServiceSchema])
async def get_services(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all services for the business."""
    result = await db.execute(
        select(Service)
        .where(Service.business_id == current_admin.business_id)
        .order_by(Service.created_at.desc())
    )
    services = result.scalars().all()
    return services


@router.post("/services", response_model=ServiceSchema, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new service."""
    new_service = Service(
        business_id=current_admin.business_id,
        name=service_data.name,
        description=service_data.description,
        price=service_data.price,
        duration_minutes=service_data.duration_minutes,
    )

    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    return new_service


@router.patch("/services/{service_id}", response_model=ServiceSchema)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a service."""
    result = await db.execute(
        select(Service).where(
            and_(
                Service.id == service_id,
                Service.business_id == current_admin.business_id,
            )
        )
    )
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    # Update only provided fields
    update_data = service_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    service.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(service)

    return service


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a service."""
    result = await db.execute(
        select(Service).where(
            and_(
                Service.id == service_id,
                Service.business_id == current_admin.business_id,
            )
        )
    )
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    await db.delete(service)
    await db.commit()


# =============================================================================
# BOOKINGS MANAGEMENT
# =============================================================================

@router.get("/bookings", response_model=list[BookingSchema])
async def get_bookings(
    status: str | None = None,
    limit: int = 50,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get bookings for the business."""
    query = select(Booking).where(Booking.business_id == current_admin.business_id)

    if status:
        query = query.where(Booking.status == BookingStatus(status))

    query = query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).limit(limit)

    result = await db.execute(query)
    bookings = result.scalars().all()

    return bookings


@router.patch("/bookings/{booking_id}", response_model=BookingSchema)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update booking status."""
    result = await db.execute(
        select(Booking).where(
            and_(
                Booking.id == booking_id,
                Booking.business_id == current_admin.business_id,
            )
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Update status
    if booking_data.status:
        booking.status = BookingStatus(booking_data.status)

    if booking_data.came_through_app is not None:
        booking.came_through_app = booking_data.came_through_app

    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    return booking


# =============================================================================
# PROMOTIONS MANAGEMENT
# =============================================================================

@router.get("/promotions", response_model=list[PromotionSchema])
async def get_promotions(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all promotions for the business."""
    result = await db.execute(
        select(Promotion)
        .where(Promotion.business_id == current_admin.business_id)
        .order_by(Promotion.created_at.desc())
    )
    promotions = result.scalars().all()
    return promotions


@router.post("/promotions", response_model=PromotionSchema, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    promotion_data: PromotionCreate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new promotion."""
    new_promotion = Promotion(
        business_id=current_admin.business_id,
        title=promotion_data.title,
        description=promotion_data.description,
        discount_percent=promotion_data.discount_percent,
        valid_from=promotion_data.valid_from,
        valid_until=promotion_data.valid_until,
    )

    db.add(new_promotion)
    await db.commit()
    await db.refresh(new_promotion)

    return new_promotion


@router.patch("/promotions/{promotion_id}", response_model=PromotionSchema)
async def update_promotion(
    promotion_id: int,
    promotion_data: PromotionUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a promotion."""
    result = await db.execute(
        select(Promotion).where(
            and_(
                Promotion.id == promotion_id,
                Promotion.business_id == current_admin.business_id,
            )
        )
    )
    promotion = result.scalar_one_or_none()

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found",
        )

    # Update only provided fields
    update_data = promotion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(promotion, field, value)

    await db.commit()
    await db.refresh(promotion)

    return promotion


@router.delete("/promotions/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: int,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a promotion."""
    result = await db.execute(
        select(Promotion).where(
            and_(
                Promotion.id == promotion_id,
                Promotion.business_id == current_admin.business_id,
            )
        )
    )
    promotion = result.scalar_one_or_none()

    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found",
        )

    await db.delete(promotion)
    await db.commit()


# =============================================================================
# ANALYTICS
# =============================================================================

@router.get("/analytics")
async def get_analytics(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for the business."""
    # Total bookings
    total_bookings_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.business_id == current_admin.business_id)
    )
    total_bookings = total_bookings_result.scalar()

    # Bookings by status
    bookings_by_status_result = await db.execute(
        select(Booking.status, func.count(Booking.id))
        .where(Booking.business_id == current_admin.business_id)
        .group_by(Booking.status)
    )
    bookings_by_status = {
        status.value: count for status, count in bookings_by_status_result.all()
    }

    # Bookings through app
    through_app_result = await db.execute(
        select(func.count(Booking.id))
        .where(
            and_(
                Booking.business_id == current_admin.business_id,
                Booking.came_through_app == True,
            )
        )
    )
    through_app = through_app_result.scalar()

    # Total services
    total_services_result = await db.execute(
        select(func.count(Service.id))
        .where(
            and_(
                Service.business_id == current_admin.business_id,
                Service.is_active == True,
            )
        )
    )
    total_services = total_services_result.scalar()

    # Active promotions
    active_promotions_result = await db.execute(
        select(func.count(Promotion.id))
        .where(
            and_(
                Promotion.business_id == current_admin.business_id,
                Promotion.is_active == True,
                Promotion.valid_until >= datetime.utcnow(),
            )
        )
    )
    active_promotions = active_promotions_result.scalar()

    return {
        "total_bookings": total_bookings,
        "bookings_by_status": bookings_by_status,
        "bookings_through_app": through_app,
        "conversion_rate": (through_app / total_bookings * 100) if total_bookings > 0 else 0,
        "total_services": total_services,
        "active_promotions": active_promotions,
    }


# =============================================================================
# BUSINESS HOURS MANAGEMENT
# =============================================================================

@router.get("/business-hours", response_model=list[BusinessHoursResponse])
async def get_business_hours(
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get business hours for current admin's business."""
    result = await db.execute(
        select(BusinessHours)
        .where(BusinessHours.business_id == current_admin.business_id)
        .order_by(BusinessHours.day_of_week)
    )
    hours = result.scalars().all()

    # If no hours exist, create default (closed all week)
    if not hours:
        default_hours = []
        for day in range(7):
            hour = BusinessHours(
                business_id=current_admin.business_id,
                day_of_week=day,
                is_closed=True,
            )
            db.add(hour)
            default_hours.append(hour)

        await db.commit()
        for hour in default_hours:
            await db.refresh(hour)
        hours = default_hours

    return hours


@router.put("/business-hours", response_model=list[BusinessHoursResponse])
async def update_business_hours(
    hours_update: BusinessHoursBulkUpdate,
    current_admin: BusinessAdmin = Depends(get_current_business_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update business hours (all 7 days at once)."""

    # Validate that we have exactly 7 days
    if len(hours_update.hours) != 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide hours for all 7 days of the week",
        )

    # Validate day_of_week values
    days = {h.day_of_week for h in hours_update.hours}
    if days != {0, 1, 2, 3, 4, 5, 6}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide exactly one entry for each day (0-6)",
        )

    # Validate times (open_time < close_time)
    for hour in hours_update.hours:
        if not hour.is_closed and hour.open_time and hour.close_time:
            if hour.open_time >= hour.close_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Opening time must be before closing time for day {hour.day_of_week}",
                )

    # Delete existing hours
    await db.execute(
        delete(BusinessHours).where(BusinessHours.business_id == current_admin.business_id)
    )

    # Create new hours
    new_hours = []
    for hour_data in hours_update.hours:
        hour = BusinessHours(
            business_id=current_admin.business_id,
            day_of_week=hour_data.day_of_week,
            open_time=hour_data.open_time,
            close_time=hour_data.close_time,
            is_closed=hour_data.is_closed,
        )
        db.add(hour)
        new_hours.append(hour)

    await db.commit()

    # Refresh to get IDs
    for hour in new_hours:
        await db.refresh(hour)

    return new_hours
