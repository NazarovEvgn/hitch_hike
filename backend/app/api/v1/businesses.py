from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.business import Business, BusinessStatus, BusinessType
from app.models.service import Service
from app.models.promotion import Promotion
from app.models.favorite import Favorite
from app.schemas.business import Business as BusinessSchema
from app.schemas.service import Service as ServiceSchema
from app.schemas.promotion import Promotion as PromotionSchema

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessSchema])
async def get_businesses(
    business_type: Optional[str] = None,
    search: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: float = 10.0,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of businesses with filters.

    Filters:
    - business_type: car_wash, repair_shop, tire_service
    - search: search by name or description
    - lat, lon: filter by location (requires both)
    - radius_km: radius in kilometers (default 10km)
    - limit: max results (default 50, max 100)
    - offset: pagination offset
    """
    query = select(Business)

    # Filter by type
    if business_type:
        try:
            query = query.where(Business.type == BusinessType(business_type))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid business_type. Must be one of: car_wash, repair_shop, tire_service",
            )

    # Search by name or description
    if search:
        search_filter = or_(
            Business.name.ilike(f"%{search}%"),
            Business.description.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Filter by location (simple distance calculation)
    # Note: For production, use PostGIS for better performance
    if lat is not None and lon is not None:
        # Haversine formula approximation
        # This is a simplified version, for production use PostGIS
        lat_range = radius_km / 111.0  # ~111 km per degree latitude
        lon_range = radius_km / (111.0 * func.cos(func.radians(lat)))

        query = query.where(
            and_(
                Business.lat.between(lat - lat_range, lat + lat_range),
                Business.lon.between(lon - lon_range, lon + lon_range),
            )
        )

    # Order by name
    query = query.order_by(Business.name).limit(limit).offset(offset)

    result = await db.execute(query)
    businesses = result.scalars().all()

    return businesses


@router.get("/nearby")
async def get_nearby_businesses(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    business_type: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    Get businesses near a specific location with their current status.

    Returns businesses sorted by distance with status information.
    """
    # Get businesses near location
    businesses_result = await get_businesses(
        business_type=business_type,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        limit=limit,
        db=db,
    )

    # Fetch status for each business
    business_ids = [b.id for b in businesses_result]
    statuses_result = await db.execute(
        select(BusinessStatus).where(BusinessStatus.business_id.in_(business_ids))
    )
    statuses = {s.business_id: s for s in statuses_result.scalars().all()}

    # Combine business data with status
    result = []
    for business in businesses_result:
        business_dict = {
            "id": business.id,
            "name": business.name,
            "type": business.type.value,
            "address": business.address,
            "lat": business.lat,
            "lon": business.lon,
            "phone": business.phone,
            "description": business.description,
            "logo_url": business.logo_url,
        }

        # Add status if exists
        if business.id in statuses:
            st = statuses[business.id]
            business_dict["status"] = {
                "status": st.status.value,
                "estimated_wait_minutes": st.estimated_wait_minutes,
                "current_queue_count": st.current_queue_count,
                "updated_at": st.updated_at,
            }
        else:
            business_dict["status"] = {
                "status": "available",
                "estimated_wait_minutes": 0,
                "current_queue_count": 0,
                "updated_at": None,
            }

        result.append(business_dict)

    return result


@router.get("/{business_id}")
async def get_business_details(
    business_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific business."""
    # Get business
    business_result = await db.execute(select(Business).where(Business.id == business_id))
    business = business_result.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    # Get current status
    status_result = await db.execute(
        select(BusinessStatus).where(BusinessStatus.business_id == business_id)
    )
    business_status = status_result.scalar_one_or_none()

    # Get services
    services_result = await db.execute(
        select(Service).where(
            and_(Service.business_id == business_id, Service.is_active == True)
        )
    )
    services = services_result.scalars().all()

    # Get active promotions
    promotions_result = await db.execute(
        select(Promotion).where(
            and_(
                Promotion.business_id == business_id,
                Promotion.is_active == True,
                Promotion.valid_until >= func.now(),
            )
        )
    )
    promotions = promotions_result.scalars().all()

    return {
        "id": business.id,
        "name": business.name,
        "type": business.type.value,
        "address": business.address,
        "lat": business.lat,
        "lon": business.lon,
        "phone": business.phone,
        "email": business.email,
        "description": business.description,
        "logo_url": business.logo_url,
        "status": {
            "status": business_status.status.value if business_status else "available",
            "estimated_wait_minutes": (
                business_status.estimated_wait_minutes if business_status else 0
            ),
            "current_queue_count": (
                business_status.current_queue_count if business_status else 0
            ),
            "updated_at": business_status.updated_at if business_status else None,
        },
        "services": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "price": s.price,
                "duration_minutes": s.duration_minutes,
            }
            for s in services
        ],
        "promotions": [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "discount_percent": p.discount_percent,
                "valid_from": p.valid_from,
                "valid_until": p.valid_until,
            }
            for p in promotions
        ],
    }


@router.get("/{business_id}/services", response_model=list[ServiceSchema])
async def get_business_services(
    business_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all active services for a business."""
    result = await db.execute(
        select(Service).where(
            and_(Service.business_id == business_id, Service.is_active == True)
        )
    )
    services = result.scalars().all()
    return services


@router.get("/{business_id}/promotions", response_model=list[PromotionSchema])
async def get_business_promotions(
    business_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all active promotions for a business."""
    result = await db.execute(
        select(Promotion).where(
            and_(
                Promotion.business_id == business_id,
                Promotion.is_active == True,
                Promotion.valid_until >= func.now(),
            )
        )
    )
    promotions = result.scalars().all()
    return promotions
