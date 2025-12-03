"""
Скрипт для очистки БД и добавления салонов красоты для тестирования.

Добавляет:
1. Салон красоты "Familia" - 2 точки (сеть)
2. Салон-парикмахерская "Голливуд" - 1 точка
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from argon2 import PasswordHasher

# Установка кодировки для консоли Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from app.core.database import async_session_maker
from app.models.business import (
    Business,
    BusinessType,
    BusinessAdmin,
    BusinessStatus,
    BusinessHours,
    StatusHistory,
    SubscriptionStatus,
    AvailabilityStatus,
)
from app.models.service import Service
from app.models.booking import Booking
from app.models.favorite import Favorite
from app.models.promotion import Promotion

ph = PasswordHasher()


async def clear_database():
    """Очистка всех данных из БД."""
    print("Очистка базы данных...")

    async with async_session_maker() as session:
        # Удаляем в правильном порядке (учитывая foreign keys)
        await session.execute(delete(Booking))
        await session.execute(delete(Favorite))
        await session.execute(delete(Promotion))
        await session.execute(delete(Service))
        await session.execute(delete(BusinessStatus))
        await session.execute(delete(StatusHistory))  # Добавлено
        await session.execute(delete(BusinessHours))
        await session.execute(delete(BusinessAdmin))
        await session.execute(delete(Business))

        await session.commit()

    print("OK: База данных очищена")


async def create_business_with_admin(
    name: str,
    address: str,
    lat: float,
    lon: float,
    phone: str,
    email: str,
    password: str,
    description: str = None,
):
    """Создание бизнеса с администратором и начальными настройками."""

    async with async_session_maker() as session:
        # Создаем бизнес
        business = Business(
            name=name,
            type=BusinessType.BEAUTY_SALON,
            address=address,
            lat=lat,
            lon=lon,
            phone=phone,
            email=email,
            description=description,
            subscription_status=SubscriptionStatus.TRIAL,
            subscription_end_date=datetime.utcnow() + timedelta(days=90),  # 3 месяца
        )
        session.add(business)
        await session.flush()

        # Создаем администратора
        admin = BusinessAdmin(
            business_id=business.id,
            email=email,
            password_hash=ph.hash(password),
            role="owner",
        )
        session.add(admin)

        # Создаем начальный статус
        status = BusinessStatus(
            business_id=business.id,
            status=AvailabilityStatus.AVAILABLE,
            estimated_wait_minutes=0,
        )
        session.add(status)

        # Создаем рабочие часы (пн-сб 9:00-20:00, вс - выходной)
        for day in range(7):
            if day == 6:  # Воскресенье
                hours = BusinessHours(
                    business_id=business.id,
                    day_of_week=day,
                    is_closed=True,
                )
            else:
                hours = BusinessHours(
                    business_id=business.id,
                    day_of_week=day,
                    open_time=datetime.strptime("09:00", "%H:%M").time(),
                    close_time=datetime.strptime("20:00", "%H:%M").time(),
                    is_closed=False,
                )
            session.add(hours)

        await session.commit()

        print(f"OK: Создан {name} ({address})")
        print(f"   Email: {email}, Password: {password}")

        return business.id


async def seed_data():
    """Добавление тестовых данных."""
    print("\nДобавление салонов красоты...\n")

    # 1. Салон красоты "Familia" - Точка 1
    # URL: https://2gis.ru/tyumen/search/салон%20красоты/firm/70000001028733869?m=65.555162%2C57.11383%2F17
    await create_business_with_admin(
        name="Familia",
        address="ул. Менделеева, д. 5, Тюмень",
        lat=57.11383,  # latitude (широта)
        lon=65.555162,  # longitude (долгота)
        phone="+7 (3452) 555-001",
        email="familia.mendeleeva@example.com",
        password="Familia123",
        description="Сеть салонов красоты Familia. Профессиональные мастера, современное оборудование.",
    )

    # 2. Салон красоты "Familia" - Точка 2
    # URL: https://2gis.ru/tyumen/branches/70000001028733868/firm/70000001055134648/65.65779%2C57.177852
    await create_business_with_admin(
        name="Familia",
        address="ул. Тимофея Чаркова, д. 83, Тюмень",
        lat=57.177852,  # latitude (широта)
        lon=65.65779,  # longitude (долгота)
        phone="+7 (3452) 555-002",
        email="familia.charkova@example.com",
        password="Familia123",
        description="Сеть салонов красоты Familia. Профессиональные мастера, современное оборудование.",
    )

    # 3. Салон-парикмахерская "Голливуд"
    # URL: https://2gis.ru/tyumen/search/парикмахерская%20голливуд/firm/1830115630041025/65.48677%2C57.147759
    await create_business_with_admin(
        name="Голливуд",
        address="ул. Восстания, д. 19, Тюмень",
        lat=57.147759,  # latitude (широта)
        lon=65.48677,  # longitude (долгота)
        phone="+7 (3452) 555-003",
        email="hollywood.salon@example.com",
        password="Hollywood123",
        description="Салон-парикмахерская с опытными стилистами. Стрижки, окрашивание, укладки.",
    )

    print("\nОК: Все данные добавлены!")
    print("\nТестовые аккаунты:")
    print("   1. familia.mendeleeva@example.com / Familia123")
    print("   2. familia.charkova@example.com / Familia123")
    print("   3. hollywood.salon@example.com / Hollywood123")


async def main():
    """Главная функция."""
    print("="*60)
    print("Обновление базы данных")
    print("="*60)

    await clear_database()
    await seed_data()

    print("\n" + "="*60)
    print("Обновление завершено!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
