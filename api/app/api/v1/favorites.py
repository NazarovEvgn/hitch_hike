from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.business import Business
from app.models.favorite import Favorite

router = APIRouter(prefix="/favorites", tags=["favorites"])


class FavoriteCreate(BaseModel):
    business_id: int


class FavoriteResponse(BaseModel):
    id: int
    business_id: int
    business_name: str
    business_type: str

    class Config:
        from_attributes = True


@router.get("/my", response_model=list[FavoriteResponse])
async def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all favorites for the authenticated user."""
    result = await db.execute(
        select(Favorite, Business)
        .join(Business, Favorite.business_id == Business.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )

    favorites = []
    for favorite, business in result.all():
        favorites.append(
            {
                "id": favorite.id,
                "business_id": business.id,
                "business_name": business.name,
                "business_type": business.type.value,
            }
        )

    return favorites


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a business to favorites."""
    # Check if business exists
    business_result = await db.execute(
        select(Business).where(Business.id == favorite_data.business_id)
    )
    business = business_result.scalar_one_or_none()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    # Check if already in favorites
    existing_result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.business_id == favorite_data.business_id,
            )
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business already in favorites",
        )

    # Add to favorites
    new_favorite = Favorite(
        user_id=current_user.id,
        business_id=favorite_data.business_id,
    )

    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    return {
        "success": True,
        "message": "Business added to favorites",
        "favorite_id": new_favorite.id,
    }


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a business from favorites."""
    result = await db.execute(
        select(Favorite).where(
            and_(Favorite.id == favorite_id, Favorite.user_id == current_user.id)
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    await db.delete(favorite)
    await db.commit()


@router.delete("/business/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_by_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a business from favorites by business_id."""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.business_id == business_id,
                Favorite.user_id == current_user.id,
            )
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    await db.delete(favorite)
    await db.commit()
