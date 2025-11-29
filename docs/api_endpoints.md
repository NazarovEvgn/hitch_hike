# API Endpoints Documentation - ХичХайк

Полная документация всех API endpoints backend приложения.

**Base URL:** `http://localhost:8000/api/v1`

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Admin Endpoints](#admin-endpoints)
3. [Client Endpoints - Businesses](#client-endpoints---businesses)
4. [Client Endpoints - Bookings](#client-endpoints---bookings)
5. [Client Endpoints - Favorites](#client-endpoints---favorites)

---

## Authentication

### POST `/auth/register/client`
Register a new client user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Иван Иванов",
  "phone": "+79001234567"  // optional
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

### POST `/auth/register/business`
Register a new business with admin account.

**Request Body:**
```json
{
  "email": "admin@carwash.com",
  "password": "securepassword",
  "business_name": "Автомойка Премиум",
  "business_type": "car_wash",  // car_wash | repair_shop | tire_service
  "address": "ул. Ленина, 10",
  "lat": 57.152985,
  "lon": 65.534328,
  "phone": "+79001234567",
  "business_email": "info@carwash.com",  // optional
  "description": "Лучшая автомойка в городе"  // optional
}
```

**Response:** `201 Created` (same as client registration)

---

### POST `/auth/login/client`
Login for client users.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK` (same token structure)

---

### POST `/auth/login/business`
Login for business administrators.

**Request Body:**
```json
{
  "email": "admin@carwash.com",
  "password": "securepassword"
}
```

**Response:** `200 OK` (same token structure)

---

## Admin Endpoints

**Authentication Required:** All admin endpoints require `Authorization: Bearer <access_token>` header with business admin token.

---

### Business Profile

#### GET `/admin/business/profile`
Get business profile for current admin.

**Response:**
```json
{
  "id": 1,
  "name": "Автомойка Премиум",
  "type": "car_wash",
  "address": "ул. Ленина, 10",
  "lat": 57.152985,
  "lon": 65.534328,
  "phone": "+79001234567",
  "email": "info@carwash.com",
  "description": "Лучшая автомойка в городе",
  "logo_url": null,
  "dgis_id": null,
  "subscription_status": "trial",
  "subscription_end_date": "2025-02-27T12:00:00",
  "created_at": "2025-11-29T12:00:00",
  "updated_at": "2025-11-29T12:00:00"
}
```

#### PATCH `/admin/business/profile`
Update business profile.

**Request Body:**
```json
{
  "name": "Автомойка Премиум Плюс",  // optional
  "address": "ул. Ленина, 12",  // optional
  "phone": "+79009999999",  // optional
  "email": "new@email.com",  // optional
  "description": "Новое описание",  // optional
  "logo_url": "https://example.com/logo.png"  // optional
}
```

---

### Status Management

#### PATCH `/admin/status`
Update business availability status.

**Request Body:**
```json
{
  "status": "busy",  // available | busy | very_busy
  "estimated_wait_minutes": 20,
  "current_queue_count": 3
}
```

**Response:**
```json
{
  "success": true,
  "status": "busy",
  "estimated_wait_minutes": 20,
  "updated_at": "2025-11-29T14:30:00"
}
```

#### GET `/admin/status/current`
Get current business status.

**Response:**
```json
{
  "status": "busy",
  "estimated_wait_minutes": 20,
  "current_queue_count": 3,
  "updated_at": "2025-11-29T14:30:00"
}
```

#### GET `/admin/status/history?limit=50`
Get status update history.

**Query Parameters:**
- `limit`: Number of records (default: 50)

**Response:**
```json
[
  {
    "status": "busy",
    "estimated_wait_minutes": 20,
    "updated_at": "2025-11-29T14:30:00"
  },
  {
    "status": "available",
    "estimated_wait_minutes": 0,
    "updated_at": "2025-11-29T12:00:00"
  }
]
```

---

### Services Management

#### GET `/admin/services`
Get all services for the business.

**Response:**
```json
[
  {
    "id": 1,
    "business_id": 1,
    "name": "Комплексная мойка",
    "description": "Полная мойка автомобиля",
    "price": 500.0,
    "duration_minutes": 30,
    "is_active": true,
    "created_at": "2025-11-29T12:00:00",
    "updated_at": "2025-11-29T12:00:00"
  }
]
```

#### POST `/admin/services`
Create a new service.

**Request Body:**
```json
{
  "name": "Экспресс мойка",
  "description": "Быстрая мойка за 15 минут",
  "price": 300.0,
  "duration_minutes": 15
}
```

**Response:** `201 Created` (service object)

#### PATCH `/admin/services/{service_id}`
Update a service.

**Request Body:** (all fields optional)
```json
{
  "name": "Экспресс мойка PRO",
  "description": "Обновленное описание",
  "price": 350.0,
  "duration_minutes": 20,
  "is_active": false
}
```

**Response:** `200 OK` (updated service object)

#### DELETE `/admin/services/{service_id}`
Delete a service.

**Response:** `204 No Content`

---

### Bookings Management

#### GET `/admin/bookings?status=pending&limit=50`
Get bookings for the business.

**Query Parameters:**
- `status`: Filter by status (pending|confirmed|completed|cancelled)
- `limit`: Number of records (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "business_id": 1,
    "user_id": 2,
    "service_id": 1,
    "booking_date": "2025-11-30",
    "booking_time": "14:00:00",
    "status": "pending",
    "client_name": "Петр Петров",
    "client_phone": "+79001111111",
    "notes": "Срочная мойка",
    "came_through_app": true,
    "created_at": "2025-11-29T12:00:00",
    "updated_at": "2025-11-29T12:00:00"
  }
]
```

#### PATCH `/admin/bookings/{booking_id}`
Update booking status.

**Request Body:**
```json
{
  "status": "confirmed",  // pending | confirmed | completed | cancelled
  "came_through_app": true  // optional
}
```

**Response:** `200 OK` (updated booking object)

---

### Promotions Management

#### GET `/admin/promotions`
Get all promotions for the business.

**Response:**
```json
[
  {
    "id": 1,
    "business_id": 1,
    "title": "Скидка 20%",
    "description": "На все услуги в будние дни",
    "discount_percent": 20,
    "valid_from": "2025-11-29T00:00:00",
    "valid_until": "2025-12-31T23:59:59",
    "is_active": true,
    "created_at": "2025-11-29T12:00:00"
  }
]
```

#### POST `/admin/promotions`
Create a new promotion.

**Request Body:**
```json
{
  "title": "Скидка 20%",
  "description": "На все услуги в будние дни",
  "discount_percent": 20,
  "valid_from": "2025-11-29T00:00:00",
  "valid_until": "2025-12-31T23:59:59"
}
```

**Response:** `201 Created` (promotion object)

#### PATCH `/admin/promotions/{promotion_id}`
Update a promotion.

**Request Body:** (all fields optional)
```json
{
  "title": "Скидка 30%",
  "description": "Обновленное описание",
  "discount_percent": 30,
  "valid_from": "2025-12-01T00:00:00",
  "valid_until": "2025-12-31T23:59:59",
  "is_active": false
}
```

**Response:** `200 OK` (updated promotion object)

#### DELETE `/admin/promotions/{promotion_id}`
Delete a promotion.

**Response:** `204 No Content`

---

### Analytics

#### GET `/admin/analytics`
Get analytics for the business.

**Response:**
```json
{
  "total_bookings": 150,
  "bookings_by_status": {
    "pending": 10,
    "confirmed": 30,
    "completed": 100,
    "cancelled": 10
  },
  "bookings_through_app": 120,
  "conversion_rate": 80.0,
  "total_services": 5,
  "active_promotions": 2
}
```

---

## Client Endpoints - Businesses

**Authentication:** Optional (some endpoints work without auth)

---

### GET `/businesses`
Get list of businesses with filters.

**Query Parameters:**
- `business_type`: Filter by type (car_wash|repair_shop|tire_service)
- `search`: Search by name or description
- `lat`, `lon`: Location filter (both required)
- `radius_km`: Radius in kilometers (default: 10)
- `limit`: Max results (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)

**Example:**
```
GET /businesses?business_type=car_wash&lat=57.152985&lon=65.534328&radius_km=5&limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Автомойка Премиум",
    "type": "car_wash",
    "address": "ул. Ленина, 10",
    "lat": 57.152985,
    "lon": 65.534328,
    "phone": "+79001234567",
    "email": "info@carwash.com",
    "description": "Лучшая автомойка в городе",
    "logo_url": null,
    "dgis_id": null,
    "subscription_status": "trial",
    "subscription_end_date": "2025-02-27T12:00:00",
    "created_at": "2025-11-29T12:00:00",
    "updated_at": "2025-11-29T12:00:00"
  }
]
```

---

### GET `/businesses/nearby`
Get businesses near a specific location with their current status.

**Query Parameters:**
- `lat`: Latitude (required)
- `lon`: Longitude (required)
- `radius_km`: Radius in kilometers (default: 5)
- `business_type`: Filter by type (optional)
- `limit`: Max results (default: 20)

**Example:**
```
GET /businesses/nearby?lat=57.152985&lon=65.534328&radius_km=5&business_type=car_wash
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Автомойка Премиум",
    "type": "car_wash",
    "address": "ул. Ленина, 10",
    "lat": 57.152985,
    "lon": 65.534328,
    "phone": "+79001234567",
    "description": "Лучшая автомойка в городе",
    "logo_url": null,
    "status": {
      "status": "busy",
      "estimated_wait_minutes": 20,
      "current_queue_count": 3,
      "updated_at": "2025-11-29T14:30:00"
    }
  }
]
```

---

### GET `/businesses/{business_id}`
Get detailed information about a specific business.

**Response:**
```json
{
  "id": 1,
  "name": "Автомойка Премиум",
  "type": "car_wash",
  "address": "ул. Ленина, 10",
  "lat": 57.152985,
  "lon": 65.534328,
  "phone": "+79001234567",
  "email": "info@carwash.com",
  "description": "Лучшая автомойка в городе",
  "logo_url": null,
  "status": {
    "status": "busy",
    "estimated_wait_minutes": 20,
    "current_queue_count": 3,
    "updated_at": "2025-11-29T14:30:00"
  },
  "services": [
    {
      "id": 1,
      "name": "Комплексная мойка",
      "description": "Полная мойка автомобиля",
      "price": 500.0,
      "duration_minutes": 30
    }
  ],
  "promotions": [
    {
      "id": 1,
      "title": "Скидка 20%",
      "description": "На все услуги в будние дни",
      "discount_percent": 20,
      "valid_from": "2025-11-29T00:00:00",
      "valid_until": "2025-12-31T23:59:59"
    }
  ]
}
```

---

### GET `/businesses/{business_id}/services`
Get all active services for a business.

**Response:**
```json
[
  {
    "id": 1,
    "business_id": 1,
    "name": "Комплексная мойка",
    "description": "Полная мойка автомобиля",
    "price": 500.0,
    "duration_minutes": 30,
    "is_active": true,
    "created_at": "2025-11-29T12:00:00",
    "updated_at": "2025-11-29T12:00:00"
  }
]
```

---

### GET `/businesses/{business_id}/promotions`
Get all active promotions for a business.

**Response:** (same structure as promotions list)

---

## Client Endpoints - Bookings

**Authentication:** Optional for creating, required for viewing own bookings

---

### POST `/bookings`
Create a new booking.

**Authentication:** Optional (works for guests and authenticated users)

**Request Body:**
```json
{
  "business_id": 1,
  "service_id": 1,
  "booking_date": "2025-11-30",
  "booking_time": "14:00:00",
  "client_name": "Петр Петров",
  "client_phone": "+79001111111",
  "notes": "Срочная мойка"  // optional
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "business_id": 1,
  "user_id": 2,  // or null for guests
  "service_id": 1,
  "booking_date": "2025-11-30",
  "booking_time": "14:00:00",
  "status": "pending",
  "client_name": "Петр Петров",
  "client_phone": "+79001111111",
  "notes": "Срочная мойка",
  "came_through_app": true,
  "created_at": "2025-11-29T12:00:00",
  "updated_at": "2025-11-29T12:00:00"
}
```

---

### GET `/bookings/my`
Get all bookings for the authenticated user.

**Authentication:** Required

**Response:** Array of booking objects

---

### GET `/bookings/{booking_id}`
Get a specific booking.

**Authentication:** Required

**Response:** Booking object

---

### PATCH `/bookings/{booking_id}/cancel`
Cancel a booking.

**Authentication:** Required

**Response:** Updated booking object with status "cancelled"

---

## Client Endpoints - Favorites

**Authentication:** Required for all favorites endpoints

---

### GET `/favorites/my`
Get all favorites for the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "business_id": 1,
    "business_name": "Автомойка Премиум",
    "business_type": "car_wash"
  }
]
```

---

### POST `/favorites`
Add a business to favorites.

**Request Body:**
```json
{
  "business_id": 1
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Business added to favorites",
  "favorite_id": 1
}
```

---

### DELETE `/favorites/{favorite_id}`
Remove a business from favorites by favorite ID.

**Response:** `204 No Content`

---

### DELETE `/favorites/business/{business_id}`
Remove a business from favorites by business ID.

**Response:** `204 No Content`

---

## Error Responses

All endpoints return consistent error format:

**400 Bad Request:**
```json
{
  "detail": "Invalid business_type. Must be one of: car_wash, repair_shop, tire_service"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found:**
```json
{
  "detail": "Business not found"
}
```

---

## API Summary

**Total Endpoints:** 35+

### By Category:
- **Authentication:** 4 endpoints
- **Admin - Business:** 2 endpoints
- **Admin - Status:** 3 endpoints
- **Admin - Services:** 4 endpoints
- **Admin - Bookings:** 2 endpoints
- **Admin - Promotions:** 4 endpoints
- **Admin - Analytics:** 1 endpoint
- **Client - Businesses:** 5 endpoints
- **Client - Bookings:** 4 endpoints
- **Client - Favorites:** 4 endpoints

---

## Testing with cURL

### Register and Login:
```bash
# Register client
curl -X POST http://localhost:8000/api/v1/auth/register/client \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/client \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

### Use Token:
```bash
# Get businesses (requires token for some endpoints)
curl http://localhost:8000/api/v1/businesses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Next Steps

- **WebSocket endpoints** for real-time updates
- **Pagination** for large result sets
- **Rate limiting** for API protection
- **API versioning** (v2) for future changes
