from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.models.business import Business, BusinessAdmin, BusinessStatus, AvailabilityStatus
from app.schemas.auth import (
    Token,
    UserLogin,
    UserRegister,
    BusinessAdminLogin,
    BusinessAdminRegister,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/client", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_client(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new client user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create tokens
    access_token = create_access_token(subject=new_user.id)
    refresh_token = create_refresh_token(subject=new_user.id)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register/business", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_business(
    business_data: BusinessAdminRegister, db: AsyncSession = Depends(get_db)
):
    """Register a new business with admin account."""
    # Check if admin email already exists
    result = await db.execute(
        select(BusinessAdmin).where(BusinessAdmin.email == business_data.email)
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create business
    new_business = Business(
        name=business_data.business_name,
        type=business_data.business_type,
        address=business_data.address,
        lat=business_data.lat,
        lon=business_data.lon,
        phone=business_data.phone,
        email=business_data.business_email,
        description=business_data.description,
        subscription_end_date=datetime.utcnow() + timedelta(days=90),  # 3 month trial
    )

    db.add(new_business)
    await db.flush()  # Get business ID

    # Create business admin
    new_admin = BusinessAdmin(
        business_id=new_business.id,
        email=business_data.email,
        password_hash=get_password_hash(business_data.password),
    )

    db.add(new_admin)
    await db.flush()

    # Create initial business status
    initial_status = BusinessStatus(
        business_id=new_business.id,
        status=AvailabilityStatus.AVAILABLE,
        updated_by_admin_id=new_admin.id,
    )

    db.add(initial_status)
    await db.commit()
    await db.refresh(new_admin)

    # Create tokens with user_type flag
    access_token = create_access_token(subject=new_admin.id, user_type="business_admin")
    refresh_token = create_refresh_token(subject=new_admin.id)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login/client", response_model=Token)
async def login_client(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login for client users."""
    # Get user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login/business", response_model=Token)
async def login_business_admin(
    credentials: BusinessAdminLogin, db: AsyncSession = Depends(get_db)
):
    """Login for business administrators."""
    # Get admin by email
    result = await db.execute(
        select(BusinessAdmin).where(BusinessAdmin.email == credentials.email)
    )
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens with user_type flag
    access_token = create_access_token(subject=admin.id, user_type="business_admin")
    refresh_token = create_refresh_token(subject=admin.id)

    return Token(access_token=access_token, refresh_token=refresh_token)
