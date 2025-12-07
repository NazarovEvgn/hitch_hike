"""initial migration

Revision ID: 001
Revises:
Create Date: 2025-11-29 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ENUM types will be created automatically by SQLAlchemy when creating tables

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Businesses table
    op.create_table('businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('car_wash', 'repair_shop', 'tire_service', name='businesstype'), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('dgis_id', sa.String(length=100), nullable=True),
        sa.Column('subscription_status', sa.Enum('trial', 'active', 'expired', 'cancelled', name='subscriptionstatus'), nullable=False),
        sa.Column('subscription_end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_businesses_id'), 'businesses', ['id'], unique=False)
    op.create_index(op.f('ix_businesses_name'), 'businesses', ['name'], unique=False)
    op.create_index(op.f('ix_businesses_dgis_id'), 'businesses', ['dgis_id'], unique=False)

    # Business admins table
    op.create_table('business_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_admins_id'), 'business_admins', ['id'], unique=False)
    op.create_index(op.f('ix_business_admins_email'), 'business_admins', ['email'], unique=True)
    op.create_index(op.f('ix_business_admins_business_id'), 'business_admins', ['business_id'], unique=False)

    # Services table
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)
    op.create_index(op.f('ix_services_business_id'), 'services', ['business_id'], unique=False)

    # Business status table
    op.create_table('business_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('available', 'busy', 'very_busy', name='availabilitystatus'), nullable=False),
        sa.Column('estimated_wait_minutes', sa.Integer(), nullable=False),
        sa.Column('current_queue_count', sa.Integer(), nullable=False),
        sa.Column('updated_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['updated_by_admin_id'], ['business_admins.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_status_id'), 'business_status', ['id'], unique=False)
    op.create_index(op.f('ix_business_status_business_id'), 'business_status', ['business_id'], unique=True)

    # Status history table
    op.create_table('status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('available', 'busy', 'very_busy', name='availabilitystatus'), nullable=False),
        sa.Column('estimated_wait_minutes', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_status_history_id'), 'status_history', ['id'], unique=False)
    op.create_index(op.f('ix_status_history_business_id'), 'status_history', ['business_id'], unique=False)
    op.create_index(op.f('ix_status_history_updated_at'), 'status_history', ['updated_at'], unique=False)

    # Bookings table
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('booking_time', sa.Time(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'completed', 'cancelled', name='bookingstatus'), nullable=False),
        sa.Column('client_name', sa.String(length=255), nullable=False),
        sa.Column('client_phone', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('came_through_app', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_business_id'), 'bookings', ['business_id'], unique=False)
    op.create_index(op.f('ix_bookings_user_id'), 'bookings', ['user_id'], unique=False)
    op.create_index(op.f('ix_bookings_service_id'), 'bookings', ['service_id'], unique=False)
    op.create_index(op.f('ix_bookings_booking_date'), 'bookings', ['booking_date'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)

    # Favorites table
    op.create_table('favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'business_id', name='uq_user_business')
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)
    op.create_index(op.f('ix_favorites_business_id'), 'favorites', ['business_id'], unique=False)

    # Promotions table
    op.create_table('promotions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('discount_percent', sa.Integer(), nullable=True),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promotions_id'), 'promotions', ['id'], unique=False)
    op.create_index(op.f('ix_promotions_business_id'), 'promotions', ['business_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_promotions_business_id'), table_name='promotions')
    op.drop_index(op.f('ix_promotions_id'), table_name='promotions')
    op.drop_table('promotions')

    op.drop_index(op.f('ix_favorites_business_id'), table_name='favorites')
    op.drop_index(op.f('ix_favorites_user_id'), table_name='favorites')
    op.drop_index(op.f('ix_favorites_id'), table_name='favorites')
    op.drop_table('favorites')

    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_booking_date'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_service_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_user_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_business_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')

    op.drop_index(op.f('ix_status_history_updated_at'), table_name='status_history')
    op.drop_index(op.f('ix_status_history_business_id'), table_name='status_history')
    op.drop_index(op.f('ix_status_history_id'), table_name='status_history')
    op.drop_table('status_history')

    op.drop_index(op.f('ix_business_status_business_id'), table_name='business_status')
    op.drop_index(op.f('ix_business_status_id'), table_name='business_status')
    op.drop_table('business_status')

    op.drop_index(op.f('ix_services_business_id'), table_name='services')
    op.drop_index(op.f('ix_services_id'), table_name='services')
    op.drop_table('services')

    op.drop_index(op.f('ix_business_admins_business_id'), table_name='business_admins')
    op.drop_index(op.f('ix_business_admins_email'), table_name='business_admins')
    op.drop_index(op.f('ix_business_admins_id'), table_name='business_admins')
    op.drop_table('business_admins')

    op.drop_index(op.f('ix_businesses_dgis_id'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_name'), table_name='businesses')
    op.drop_index(op.f('ix_businesses_id'), table_name='businesses')
    op.drop_table('businesses')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    op.execute("DROP TYPE bookingstatus")
    op.execute("DROP TYPE availabilitystatus")
    op.execute("DROP TYPE subscriptionstatus")
    op.execute("DROP TYPE businesstype")
