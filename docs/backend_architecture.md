# Backend Architecture - ХичХайк

Техническая документация backend-части проекта ХичХайк.

## Оглавление
- [Общая архитектура](#общая-архитектура)
- [Файловая структура](#файловая-структура)
- [Core модули](#core-модули)
- [Модели данных](#модели-данных)
- [Схемы валидации](#схемы-валидации)
- [API endpoints](#api-endpoints)
- [Аутентификация](#аутентификация)
- [База данных](#база-данных)
- [Конфигурация](#конфигурация)

---

## Общая архитектура

Backend построен на **FastAPI** с использованием современных практик:

```
┌─────────────┐
│   Client    │
│ (HTTP/WS)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   FastAPI App       │
│   (app/main.py)     │
└──────┬──────────────┘
       │
       ├──► API Routes (app/api/v1/)
       │    └─► Dependencies (app/api/dependencies.py)
       │         └─► Authentication & DB Session
       │
       ├──► Pydantic Schemas (app/schemas/)
       │    └─► Request/Response validation
       │
       ├──► SQLAlchemy Models (app/models/)
       │    └─► Database ORM
       │
       ├──► Business Logic (app/services/)
       │
       └──► Core (app/core/)
            ├─► Config
            ├─► Database
            ├─► Security (JWT, password hashing)
            └─► Redis
```

**Ключевые особенности:**
- **Async/Await**: Полностью асинхронная работа с БД (asyncpg, SQLAlchemy async)
- **Dependency Injection**: FastAPI dependencies для DB sessions и auth
- **JWT Authentication**: Access + Refresh tokens
- **Type Safety**: Pydantic V2 для валидации
- **Migration**: Alembic для версионирования схемы БД

---

## Файловая структура

```
backend/
├── app/                          # Основное приложение
│   ├── __init__.py
│   ├── main.py                   # Точка входа FastAPI
│   │
│   ├── core/                     # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py             # Настройки из .env
│   │   ├── database.py           # SQLAlchemy engine, session maker
│   │   ├── redis.py              # Redis client
│   │   └── security.py           # JWT, password hashing
│   │
│   ├── models/                   # SQLAlchemy ORM модели
│   │   ├── __init__.py
│   │   ├── user.py               # Модель пользователя (клиента)
│   │   ├── business.py           # Модели бизнеса, админа, статуса
│   │   ├── service.py            # Модель услуги
│   │   ├── booking.py            # Модель бронирования
│   │   ├── favorite.py           # Модель избранного
│   │   └── promotion.py          # Модель акций
│   │
│   ├── schemas/                  # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── auth.py               # Схемы аутентификации
│   │   ├── user.py               # Схемы пользователя
│   │   ├── business.py           # Схемы бизнеса
│   │   ├── service.py            # Схемы услуги
│   │   ├── booking.py            # Схемы бронирования
│   │   └── promotion.py          # Схемы акций
│   │
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py       # Общие dependencies (auth, DB)
│   │   └── v1/                   # API версии 1
│   │       ├── __init__.py
│   │       └── auth.py           # Endpoints аутентификации
│   │
│   └── services/                 # Бизнес-логика (пока пусто)
│       └── __init__.py
│
├── alembic/                      # Миграции БД
│   ├── versions/                 # Файлы миграций
│   │   └── 20251129_1220_initial_migration.py
│   ├── env.py                    # Alembic environment
│   └── script.py.mako            # Шаблон для новых миграций
│
├── tests/                        # Тесты (пока не реализованы)
│
├── .env                          # Переменные окружения (не в Git!)
├── .env.example                  # Пример .env файла
├── alembic.ini                   # Конфигурация Alembic
├── pyproject.toml                # Зависимости проекта (uv)
└── test_db_connection.py         # Утилита для тестирования БД
```

---

## Core модули

### 1. `app/main.py` - Точка входа

**Назначение:** Создание и настройка FastAPI приложения.

```python
# Что делает:
1. Создает экземпляр FastAPI app
2. Настраивает CORS middleware
3. Подключает API routers
4. Настраивает lifespan для startup/shutdown:
   - Startup: подключение к Redis
   - Shutdown: отключение от Redis
5. Регистрирует базовые endpoints (/, /health)
```

**Основные компоненты:**
- **CORS middleware**: Разрешает запросы с фронтенда (localhost:9000, localhost:9001)
- **Lifespan manager**: Управляет жизненным циклом приложения
- **Router включение**: `app.include_router(auth.router, prefix="/api/v1")`

**Endpoints:**
- `GET /` - Информация об API
- `GET /health` - Health check

---

### 2. `app/core/config.py` - Конфигурация

**Назначение:** Загрузка настроек из `.env` файла через Pydantic Settings.

```python
class Settings(BaseSettings):
    # Загружает переменные из .env
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    dgis_api_key: str
    allowed_origins: str
    environment: str = "development"
```

**Особенности:**
- Автоматическая валидация типов
- `allowed_origins_list` - property для парсинга CORS origins
- Singleton pattern: `settings = Settings()`

---

### 3. `app/core/database.py` - База данных

**Назначение:** Настройка SQLAlchemy async engine и session maker.

```python
# Компоненты:

1. Base класс для всех моделей:
   class Base(DeclarativeBase): pass

2. Async engine:
   engine = create_async_engine(
       settings.database_url,
       echo=True  # Логирование SQL в dev режиме
   )

3. Async session maker:
   async_session_maker = async_sessionmaker(
       engine,
       class_=AsyncSession,
       expire_on_commit=False
   )

4. Dependency для получения сессии:
   async def get_db() -> AsyncSession:
       # Используется в FastAPI endpoints
```

**Как использовать:**
```python
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

---

### 4. `app/core/redis.py` - Redis клиент

**Назначение:** Асинхронный клиент для работы с Redis.

```python
class RedisClient:
    async def connect()     # Подключение
    async def disconnect()  # Отключение
    async def get(key)      # Получить значение
    async def set(key, value, expire=3600)  # Установить
    async def delete(key)   # Удалить
```

**Использование:**
- Кэширование данных
- Хранение сессий
- Pub/Sub для WebSocket (будущее)

---

### 5. `app/core/security.py` - Безопасность

**Назначение:** JWT токены и хэширование паролей.

```python
# Функции:

1. verify_password(plain, hashed) -> bool
   # Проверка пароля через bcrypt

2. get_password_hash(password) -> str
   # Хэширование пароля

3. create_access_token(subject, expires_delta) -> str
   # Создание JWT access token
   # Payload: {sub: user_id, type: "access", exp: timestamp}

4. create_refresh_token(subject) -> str
   # Создание JWT refresh token
   # Payload: {sub: user_id, type: "refresh", exp: timestamp}

5. decode_token(token) -> dict
   # Декодирование и валидация JWT
```

**JWT структура:**
```json
{
  "sub": "123",           // User/Admin ID
  "type": "access",       // "access" или "refresh"
  "exp": 1234567890,      // Expiration timestamp
  "user_type": "client"   // Опционально для business_admin
}
```

---

## Модели данных

### Архитектура моделей

Все модели наследуются от `Base` (DeclarativeBase) и используют **SQLAlchemy 2.0 mapped_column** синтаксис.

```python
from sqlalchemy.orm import Mapped, mapped_column

class Example(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    nullable_field: Mapped[str | None] = mapped_column(nullable=True)
```

---

### 1. `app/models/user.py` - Пользователь (клиент)

**Таблица:** `users`

```python
class User(Base):
    id: int                    # Primary key
    email: str                 # Unique, indexed
    phone: str | None          # Опционально
    name: str
    password_hash: str
    created_at: datetime
    updated_at: datetime

    # Relationships:
    bookings: list[Booking]    # Бронирования пользователя
    favorites: list[Favorite]  # Избранные сервисы
```

**Назначение:** Клиенты, которые бронируют услуги.

---

### 2. `app/models/business.py` - Бизнес модели

#### 2.1. `Business` - Автосервис

**Таблица:** `businesses`

```python
class BusinessType(enum):
    CAR_WASH = "car_wash"
    REPAIR_SHOP = "repair_shop"
    TIRE_SERVICE = "tire_service"

class SubscriptionStatus(enum):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Business(Base):
    id: int
    name: str                              # Indexed
    type: BusinessType                     # ENUM
    address: str
    lat: float                             # Широта
    lon: float                             # Долгота
    phone: str
    email: str | None
    description: str | None
    logo_url: str | None
    dgis_id: str | None                    # ID в 2GIS, indexed
    subscription_status: SubscriptionStatus
    subscription_end_date: datetime | None # Конец подписки
    created_at: datetime
    updated_at: datetime

    # Relationships:
    admins: list[BusinessAdmin]
    services: list[Service]
    current_status: BusinessStatus         # One-to-one
    status_history: list[StatusHistory]
    bookings: list[Booking]
    favorites: list[Favorite]
    promotions: list[Promotion]
```

#### 2.2. `BusinessAdmin` - Администратор бизнеса

**Таблица:** `business_admins`

```python
class BusinessAdmin(Base):
    id: int
    business_id: int                # FK -> businesses.id
    email: str                      # Unique, indexed
    password_hash: str
    role: str = "admin"
    created_at: datetime

    # Relationships:
    business: Business
```

**Назначение:** Владельцы/администраторы автосервисов.

#### 2.3. `BusinessStatus` - Текущий статус

**Таблица:** `business_status`

```python
class AvailabilityStatus(enum):
    AVAILABLE = "available"      # 🟢 0-15 мин
    BUSY = "busy"               # 🟡 15-30 мин
    VERY_BUSY = "very_busy"     # 🟠 30+ мин

class BusinessStatus(Base):
    id: int
    business_id: int                    # FK, unique
    status: AvailabilityStatus
    estimated_wait_minutes: int = 0
    current_queue_count: int = 0
    updated_by_admin_id: int | None     # FK -> business_admins
    updated_at: datetime

    # Relationships:
    business: Business
```

**Назначение:** Текущая загруженность сервиса (только одна запись на бизнес).

#### 2.4. `StatusHistory` - История статусов

**Таблица:** `status_history`

```python
class StatusHistory(Base):
    id: int
    business_id: int                # FK
    status: AvailabilityStatus
    estimated_wait_minutes: int
    updated_at: datetime            # Indexed

    # Relationships:
    business: Business
```

**Назначение:** Логирование изменений статуса для аналитики.

---

### 3. `app/models/service.py` - Услуга

**Таблица:** `services`

```python
class Service(Base):
    id: int
    business_id: int           # FK -> businesses.id, indexed
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    # Relationships:
    business: Business
    bookings: list[Booking]
```

**Назначение:** Услуги, предоставляемые автосервисом (мойка, шиномонтаж и т.д.).

---

### 4. `app/models/booking.py` - Бронирование

**Таблица:** `bookings`

```python
class BookingStatus(enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Booking(Base):
    id: int
    business_id: int           # FK, indexed
    user_id: int | None        # FK, optional (гость может бронировать)
    service_id: int            # FK, indexed
    booking_date: date         # Indexed
    booking_time: time
    status: BookingStatus      # Indexed
    client_name: str
    client_phone: str
    notes: str | None
    came_through_app: bool = True  # Для аналитики
    created_at: datetime
    updated_at: datetime

    # Relationships:
    business: Business
    user: User | None
    service: Service
```

**Назначение:** Онлайн-бронирования клиентов.

---

### 5. `app/models/favorite.py` - Избранное

**Таблица:** `favorites`

```python
class Favorite(Base):
    id: int
    user_id: int               # FK, indexed
    business_id: int           # FK, indexed
    created_at: datetime

    # Unique constraint: (user_id, business_id)

    # Relationships:
    user: User
    business: Business
```

**Назначение:** Избранные сервисы пользователя.

---

### 6. `app/models/promotion.py` - Акция

**Таблица:** `promotions`

```python
class Promotion(Base):
    id: int
    business_id: int           # FK, indexed
    title: str
    description: str
    discount_percent: int | None
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    created_at: datetime

    # Relationships:
    business: Business
```

**Назначение:** Акции и скидки от автосервисов.

---

## Схемы валидации

### Архитектура схем

Используется **Pydantic V2** для валидации входящих/исходящих данных.

```python
from pydantic import BaseModel, ConfigDict

# Базовая схема (общие поля)
class UserBase(BaseModel):
    email: EmailStr
    name: str

# Создание (входящие данные)
class UserCreate(UserBase):
    password: str

# Ответ (исходящие данные)
class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
```

---

### 1. `app/schemas/auth.py` - Аутентификация

```python
# Токен ответ
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Вход клиента
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Регистрация клиента
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str | None = None

# Регистрация бизнеса (включает данные бизнеса + админа)
class BusinessAdminRegister(BaseModel):
    # Admin
    email: EmailStr
    password: str

    # Business
    business_name: str
    business_type: str
    address: str
    lat: float
    lon: float
    phone: str
    business_email: str | None = None
    description: str | None = None
```

**Назначение:** Валидация данных для регистрации и входа.

---

### 2. `app/schemas/user.py` - Пользователь

```python
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    password: str | None = None

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
```

---

### 3. `app/schemas/business.py` - Бизнес

```python
class BusinessBase(BaseModel):
    name: str
    type: str  # "car_wash", "repair_shop", "tire_service"
    address: str
    lat: float
    lon: float
    phone: str
    email: str | None = None
    description: str | None = None

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    # Все поля optional
    name: str | None = None
    address: str | None = None
    # ...

class BusinessStatusUpdate(BaseModel):
    status: str  # "available", "busy", "very_busy"
    estimated_wait_minutes: int = 0
    current_queue_count: int = 0

class Business(BusinessBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    logo_url: str | None = None
    dgis_id: str | None = None
    subscription_status: str
    subscription_end_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
```

---

## API Endpoints

### 1. `app/api/dependencies.py` - Dependencies

**Назначение:** Общие dependencies для всех endpoints.

```python
# HTTP Bearer схема для токенов
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Извлекает и валидирует JWT токен.
    Возвращает текущего пользователя из БД.
    Используется в endpoints, требующих аутентификации клиента.
    """
    # 1. Декодирует JWT токен
    # 2. Проверяет тип токена (должен быть "access")
    # 3. Извлекает user_id из payload
    # 4. Загружает User из БД
    # 5. Возвращает User или HTTPException 401

async def get_current_business_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> BusinessAdmin:
    """
    То же самое, но для бизнес-администраторов.
    Проверяет дополнительно user_type == "business_admin".
    """
```

**Использование:**
```python
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

### 2. `app/api/v1/auth.py` - Auth endpoints

**Базовый путь:** `/api/v1/auth`

#### POST `/register/client` - Регистрация клиента

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Иван Иванов",
  "phone": "+79001234567"
}
```

**Response:** `Token` (201 Created)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Процесс:**
1. Проверяет, что email не занят
2. Хэширует пароль (bcrypt)
3. Создает User в БД
4. Генерирует access + refresh токены
5. Возвращает токены

---

#### POST `/register/business` - Регистрация бизнеса

**Request:**
```json
{
  "email": "admin@carwash.com",
  "password": "securepassword",
  "business_name": "Автомойка Премиум",
  "business_type": "car_wash",
  "address": "ул. Ленина, 10",
  "lat": 57.152985,
  "lon": 65.534328,
  "phone": "+79001234567",
  "business_email": "info@carwash.com",
  "description": "Лучшая автомойка в городе"
}
```

**Response:** `Token` (201 Created)

**Процесс:**
1. Проверяет, что admin email не занят
2. Создает Business в БД
3. Создает BusinessAdmin для этого бизнеса
4. Создает начальный BusinessStatus (available)
5. Устанавливает subscription_end_date = +90 дней (trial)
6. Генерирует токены с user_type="business_admin"
7. Возвращает токены

**Важно:** Все 3 записи создаются в одной транзакции (db.commit()).

---

#### POST `/login/client` - Вход клиента

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `Token`

**Процесс:**
1. Находит User по email
2. Проверяет пароль (bcrypt)
3. Генерирует токены
4. Возвращает токены

---

#### POST `/login/business` - Вход администратора

**Request:**
```json
{
  "email": "admin@carwash.com",
  "password": "securepassword"
}
```

**Response:** `Token`

**Процесс:**
1. Находит BusinessAdmin по email
2. Проверяет пароль
3. Генерирует токены с user_type="business_admin"
4. Возвращает токены

---

## Аутентификация

### Процесс аутентификации

```
┌──────────┐                  ┌──────────┐
│  Client  │                  │  Server  │
└────┬─────┘                  └────┬─────┘
     │                             │
     │  POST /auth/login           │
     │  {email, password}          │
     │────────────────────────────>│
     │                             │ 1. Validate credentials
     │                             │ 2. Generate JWT tokens
     │                             │
     │  {access_token, refresh}    │
     │<────────────────────────────│
     │                             │
     │  GET /protected             │
     │  Header: Authorization:     │
     │  Bearer <access_token>      │
     │────────────────────────────>│
     │                             │ 3. Validate JWT
     │                             │ 4. Extract user_id
     │                             │ 5. Load user from DB
     │                             │
     │  Protected data             │
     │<────────────────────────────│
     │                             │
```

### JWT Токены

**Access Token:**
- Срок жизни: 30 минут (configurable)
- Используется для доступа к API
- Payload:
  ```json
  {
    "sub": "123",
    "type": "access",
    "exp": 1234567890,
    "user_type": "client"  // или "business_admin"
  }
  ```

**Refresh Token:**
- Срок жизни: 7 дней (configurable)
- Используется для получения нового access token
- Payload:
  ```json
  {
    "sub": "123",
    "type": "refresh",
    "exp": 1234567890
  }
  ```

**Refresh процесс** (будет реализован):
```python
@router.post("/refresh")
async def refresh_token(refresh_token: str):
    # 1. Validate refresh token
    # 2. Check type == "refresh"
    # 3. Generate new access token
    # 4. Optionally generate new refresh token
    # 5. Return new tokens
```

---

## База данных

### Схема базы данных

```
users                    businesses
├─ id (PK)              ├─ id (PK)
├─ email (UQ)           ├─ name
├─ password_hash        ├─ type (ENUM)
├─ name                 ├─ lat, lon
└─ phone                ├─ subscription_status
    │                   └─ dgis_id
    │                       │
    ├───────────────────────┼──────────┐
    │                       │          │
    ▼                       ▼          ▼
bookings            business_admins  services
├─ id              ├─ id            ├─ id
├─ user_id (FK)    ├─ business_id   ├─ business_id
├─ business_id     ├─ email (UQ)    ├─ name
├─ service_id      └─ password_hash ├─ price
├─ booking_date                      └─ duration
├─ client_name         │
└─ status              │
                       ▼
                business_status (1:1)
                ├─ id
                ├─ business_id (UQ, FK)
                ├─ status (ENUM)
                ├─ estimated_wait_minutes
                └─ updated_by_admin_id (FK)

                status_history (analytics)
                ├─ id
                ├─ business_id (FK)
                ├─ status
                └─ updated_at (indexed)
```

### Индексы

**Для производительности:**
- `users.email` - unique index (быстрый поиск при логине)
- `businesses.name` - index (поиск по названию)
- `businesses.dgis_id` - index (синхронизация с 2GIS)
- `business_admins.email` - unique index
- `bookings.booking_date` - index (фильтрация по дате)
- `bookings.status` - index (фильтрация по статусу)
- `status_history.updated_at` - index (аналитика по времени)

### ENUM типы

PostgreSQL ENUM типы для строгой типизации:

1. **businesstype**: `car_wash`, `repair_shop`, `tire_service`
2. **subscriptionstatus**: `trial`, `active`, `expired`, `cancelled`
3. **availabilitystatus**: `available`, `busy`, `very_busy`
4. **bookingstatus**: `pending`, `confirmed`, `completed`, `cancelled`

### Миграции

**Текущая миграция:** `20251129_1220_initial_migration.py`

Создана вручную из-за проблем с asyncpg подключением на Windows.

**Структура миграции:**
```python
def upgrade() -> None:
    # 1. Создание ENUM типов
    op.execute("CREATE TYPE businesstype AS ENUM (...)")

    # 2. Создание таблиц по порядку (сначала без FK)
    op.create_table('users', ...)
    op.create_table('businesses', ...)

    # 3. Создание таблиц с FK
    op.create_table('business_admins',
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'])
    )

    # 4. Создание индексов
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    # Откат в обратном порядке
```

**Версионирование:**
- Хранится в таблице `alembic_version`
- Текущая версия: `001`

---

## Конфигурация

### 1. `.env` файл

```bash
# База данных
DATABASE_URL=postgresql+asyncpg://hitchhike:hitchhike@127.0.0.1:5432/hitchhike_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=<generated-secure-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 2GIS
DGIS_API_KEY=your-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:9000,http://localhost:9001

# Environment
ENVIRONMENT=development
```

### 2. `pyproject.toml`

**Зависимости проекта:**
```toml
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "redis>=5.0.1",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
]
```

**Dev зависимости:**
```toml
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "black>=24.0.0",
]
```

### 3. `alembic.ini`

Конфигурация Alembic для миграций:
```ini
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
sqlalchemy.url = postgresql+asyncpg://hitchhike:hitchhike@127.0.0.1:5432/hitchhike_db
```

**Важно:** `sqlalchemy.url` перезаписывается в `alembic/env.py` из `settings.database_url`.

---

## Docker Compose

### Конфигурация

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: hitchhike
      POSTGRES_PASSWORD: hitchhike
      POSTGRES_DB: hitchhike_db
      POSTGRES_HOST_AUTH_METHOD: md5
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

**Особенности:**
- `POSTGRES_HOST_AUTH_METHOD: md5` - для корректной аутентификации извне
- Volumes для персистентности данных
- Health checks для проверки готовности

---

## Запуск приложения

### Development режим

```bash
# 1. Запустить БД
docker-compose up -d

# 2. Активировать venv
cd backend
.venv\Scripts\activate  # Windows

# 3. Запустить сервер
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Доступные URL:**
- API: http://127.0.0.1:8000
- Docs (Swagger): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

### Production режим

```bash
# С uvicorn workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Или с gunicorn + uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Следующие шаги

### Phase 2: Admin Panel API

**Новые endpoints для реализации:**
```python
# Business management
GET    /api/v1/admin/business/profile
PATCH  /api/v1/admin/business/profile

# Status management
PATCH  /api/v1/admin/status
GET    /api/v1/admin/status/history

# Bookings management
GET    /api/v1/admin/bookings
PATCH  /api/v1/admin/bookings/{id}

# Services management
GET    /api/v1/admin/services
POST   /api/v1/admin/services
PATCH  /api/v1/admin/services/{id}
DELETE /api/v1/admin/services/{id}

# Analytics
GET    /api/v1/admin/analytics
```

### Phase 3: Client API

```python
# Business browsing
GET    /api/v1/businesses
GET    /api/v1/businesses/{id}
GET    /api/v1/businesses/nearby

# Bookings
POST   /api/v1/bookings
GET    /api/v1/bookings/my
PATCH  /api/v1/bookings/{id}/cancel

# Favorites
POST   /api/v1/favorites
GET    /api/v1/favorites/my
DELETE /api/v1/favorites/{id}
```

### Phase 4: WebSocket

```python
# Real-time updates
WS /ws/businesses/{business_id}
WS /ws/admin/notifications
```

---

## Заключение

Backend ХичХайк построен с использованием современного стека технологий:
- **FastAPI** для высокой производительности
- **SQLAlchemy 2.0** для type-safe работы с БД
- **Pydantic V2** для валидации данных
- **JWT** для безопасной аутентификации
- **Docker** для изоляции зависимостей
- **uv** для быстрого управления пакетами

Архитектура готова к масштабированию и добавлению новых функций в следующих фазах разработки.
