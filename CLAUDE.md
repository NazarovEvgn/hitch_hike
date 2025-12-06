# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Project Status

**✅ Phase 1 Complete**: Backend infrastructure is implemented and database is ready.
**✅ Phase 2 Complete**: Full REST API with all admin and client endpoints implemented.
**✅ Phase 3 Complete**: Quasar Admin Panel with full authentication and core functionality tested.
**✅ Phase 4 Complete**: Client PWA Application - 2GIS Map Integration
**🔄 Phase 5 In Progress**: Migration to Ionic Framework + Tailwind CSS

**What's implemented:**
- ✅ FastAPI backend with uv package manager
- ✅ PostgreSQL database with all tables created (Docker port: 5433)
- ✅ SQLAlchemy 2.0 async models with proper Enum handling
- ✅ JWT authentication with user_type field (argon2 password hashing)
- ✅ Pydantic validation schemas
- ✅ Auth API endpoints (register/login for clients and business admins)
- ✅ Admin API endpoints (35+ endpoints - profile, services, bookings, analytics, status updates)
- ✅ Client API endpoints (businesses browsing, bookings, favorites)
- ✅ Docker Compose setup (PostgreSQL on port 5433, Redis on 6379)
- ✅ Database migrations with proper Enum values
- ✅ Redis integration prepared
- ✅ API documentation (see docs/api_endpoints.md)
- ✅ **Database updated** with beauty salon businesses (BEAUTY_SALON type added)
  - ✅ "Familia" (2 locations: Менделеева 137к1, Чаркова 56)
  - ✅ "Hollywood" (Тура 4/2)
  - ✅ Test accounts: familia.mendeleeva@example.com / Familia123, familia.charkova@example.com / Familia123, hollywood.salon@example.com / Hollywood123
- ✅ **Brand colors applied**: Purple #27126A (primary), Green #98EA14 (accent)
  - ✅ Client app map markers: purple circles with green "available" indicator
  - ✅ Admin panel Quasar variables configured
- ✅ **Quasar Admin Panel** (admin-app/) - http://localhost:9001
  - ✅ Login page with JWT authentication (direct API calls)
  - ✅ Main layout with purple header (bg-primary)
  - ✅ Dashboard redesigned per dev_plan.md (single toggle, compact layout)
  - ✅ Status update page (PRIMARY FEATURE) - fully functional
  - ✅ **Services page** - CRUD operations tested (create, edit, delete, toggle active)
  - ✅ **Bookings page** - Status management tested (view, filter, update status)
  - 🔄 Placeholder pages: Promotions, Analytics, Profile
  - ✅ Pinia store for auth state management
  - ✅ Axios with automatic JWT token refresh
  - ✅ Tilda Sans fonts integrated (all weights)

**❌ CRITICAL ISSUE - Business Profile Not Loading in Header:**
- **Problem**: After successful login, MainLayout header should display business name and address, but it shows empty values
- **Root Cause**: Pinia store initialization timing issue - `useAuthStore()` called before Pinia is ready
- **Attempts made**:
  1. ❌ LoginPage.vue: Dynamic import + fetchProfile() → "getActivePinia() was called but there was no active Pinia" error
  2. ❌ MainLayout.vue: onMounted() + fetchProfile() → Same Pinia error
  3. ❌ router/index.js: beforeEach guard + fetchProfile() → No error in console, but `/api/v1/admin/business/profile` endpoint never called
- **Backend Status**: `/api/v1/admin/business/profile` endpoint exists and works (tested manually returns correct data)
- **Current State**:
  - Login works ✅
  - Dashboard loads ✅
  - Status updates work ✅
  - Bookings load ✅
  - But authStore.business remains null → header shows empty strings
- **Files affected**:
  - `admin-app/src/pages/LoginPage.vue` (login logic)
  - `admin-app/src/layouts/MainLayout.vue` (header display with businessName, businessAddress computed properties)
  - `admin-app/src/stores/auth.js` (fetchProfile() method)
  - `admin-app/src/router/index.js` (router guard with fetchProfile() call)
  - `backend/app/api/v1/admin.py:25` (GET /admin/business/profile endpoint)

**Known Issues & Solutions:**
- ⚠️ **PostgreSQL Port Conflict**: If you have local PostgreSQL 17 installed, Docker uses port 5433 instead of 5432
- ✅ **Fixed**: Enum values now use lowercase (car_wash, not CAR_WASH) via `values_callable`
- ✅ **Fixed**: Password hashing switched from bcrypt to argon2-cffi for better compatibility
- ✅ **Fixed**: JWT tokens now include `user_type` field for business_admin authentication
- ✅ **Fixed**: LoginPage uses direct API calls to avoid Pinia initialization timing issues
- ✅ **Fixed**: CORS configured for multiple dev server ports (9000, 9001, 9002, 3000)
- ✅ **Fixed**: DashboardPage endpoint changed from `/admin/status` to `/admin/status/current` (405 error resolved)

**✅ Phase 4 Complete:** Client PWA Application - 2GIS Map Integration
- ✅ **Quasar PWA project created** (client-app/) - http://localhost:9002
  - ✅ Project structure with pages, routing, axios configured
  - ✅ MapPage with filter panel and business card UI
  - ✅ FavoritesPage and ErrorNotFound pages
  - ✅ PWA manifest and service worker setup
  - ✅ **2GIS MapGL integration** (branch: feature/2gis-map-integration)
- ✅ **2GIS map display with custom HTML markers**
  - ✅ Color-coded markers: 🟢 Green (available), 🟡 Orange (busy), 🔴 Red (very busy)
  - ✅ Emoji thumbs-up (👍) markers for better visibility
  - ✅ Custom marker styling with borders and shadows
- ✅ **Load and display businesses from API** via `/businesses/nearby`
  - ✅ Real-time status display (estimated wait time, queue count)
  - ✅ Automatic map updates when businesses change
- ✅ **Business card with detailed information**
  - ✅ Click on marker to show business details
  - ✅ Display: name, address, phone, status, wait time
  - ✅ Action buttons: Call, Book (placeholder)
- ✅ **Type filtering** (car wash/repair shop/tire service)
  - ✅ Filter buttons hide/show markers by business type
- ✅ **2GIS API key configuration** in quasar.config.js
- ✅ **VPN troubleshooting documentation** added
- ✅ **Real businesses added**: Автомойка Тура, Автомойка Пена (Tyumen)
- ✅ **Precise geolocation** from 2GIS URLs (lat/lon extraction)
- 🔄 Online booking form (placeholder - to be implemented)
- 🔄 Favorites functionality (placeholder - to be implemented)

**🔄 Phase 5 (In Progress):** Migration to Ionic Framework + Tailwind CSS

**Decision rationale:**
- Both admin and client apps will be used primarily on smartphones
- Quasar has good PWA support but design feels dated (Material Design ~2020)
- Ionic Framework provides modern native mobile UX (iOS 17 / Material Design 3)
- Tailwind CSS adds flexibility for custom components and brand styling

**Migration plan:**
1. **Create new Ionic projects** (admin-ionic-app/ and client-ionic-app/)
   - Use Ionic CLI with Vue 3 template
   - Install Tailwind CSS for custom styling
   - Setup Capacitor for PWA + future native builds

2. **Port backend integration**
   - Copy Pinia stores (auth, business state)
   - Setup Axios with JWT interceptors
   - Configure API base URL and CORS

3. **Rebuild UI with Ionic components + Tailwind**
   - Use Ionic components for navigation, modals, cards, lists
   - Use Tailwind for custom layouts, gradients, spacing
   - Apply brand colors via CSS Variables + Tailwind config

4. **Maintain feature parity**
   - All existing features from Quasar apps
   - Improved mobile UX with native iOS/Android styles
   - Swipe gestures, pull-to-refresh, native animations

**Technology stack:**
- **Ionic Framework 7.x** - Native mobile components
- **Vue 3 Composition API** - Same as current apps
- **Tailwind CSS 3.x** - Utility-first styling
- **Capacitor 5.x** - PWA + Native capabilities
- **Pinia** - State management (same as current)
- **Axios** - HTTP client with JWT (same as current)

**Architecture:** Feature-Based Architecture
- Each business feature (auth, bookings, services, employees, business-status, profile) is a self-contained module
- Feature structure: `components/`, `stores/`, `services/`, `pages/`, `types/`
- Shared components and utilities in `shared/` directory
- Core infrastructure (API, router, config) in `core/` directory
- No Atomic Design - keeping it simple and pragmatic

**Project structure:**
```
admin-ionic-app/
├── src/
│   ├── features/           # Business features (isolated modules)
│   │   ├── auth/
│   │   ├── bookings/
│   │   ├── services/
│   │   ├── employees/
│   │   ├── business-status/
│   │   ├── profile/
│   │   └── dashboard/
│   ├── shared/             # Reusable across features
│   │   ├── components/
│   │   ├── composables/
│   │   ├── utils/
│   │   ├── types/
│   │   └── layouts/
│   └── core/               # Infrastructure
│       ├── api/
│       ├── router/
│       └── config/
```

**Timeline estimate:** 2-3 days for both apps

**Phase 6 (Next):** Additional Features & Production Deployment
- Online booking form (no registration required for clients)
- Favorites functionality (localStorage)
- WebSocket for real-time status updates
- Complete remaining admin features (Promotions, Analytics, Advanced Profile)
- Production deployment with Capacitor PWA
- Optional: Native iOS/Android builds via Capacitor

## Project Overview

**ХичХайк** (HitchHike) - Real-Time Service Availability Platform for auto service businesses (car washes, repair shops, tire services) integrated with 2GIS maps.

**Brand:** ХичХайк
**Domains:**
- хичхайк.рф (client PWA application)
- api.хичхайк.рф (backend API)
- admin.хичхайк.рф (admin panel)

**Logo:** 👍 Thumbs up icon with color-coded availability:
- 🟢 Green = available (0-15 min wait)
- 🟡 Yellow = busy (15-30 min wait)
- 🟠 Orange = very busy (30+ min wait)

**Key Value Proposition**: Show real-time service availability on a map when clients need the service right now.

**Target Market**: Tyumen, Russia (initial MVP launch) → expand to other cities

**MVP Focus (Minimum Viable Product):**

For business owners:
1. Register business and add to map
2. Add services with prices
3. **PRIMARY FEATURE:** Update availability status (green/yellow/orange)
4. View and manage online bookings
5. Get reminders to update status

For clients (NO registration required):
1. Select service type (car wash, repair shop, tire service)
2. View map with color-coded availability markers
3. Click on marker → see info + 3 actions:
   - 📞 Call (direct tel: link)
   - 📝 Book online (simple form, no account needed)
   - 🗺️ Navigate (redirect to 2GIS with route)

**Business Model**:
- Free for clients (no registration required for MVP)
- Subscription for businesses (~1000-3000 RUB/month)
- 3-month free trial for initial businesses in Tyumen

**Hosting Cost**: ~500₽/month (Timeweb Cloud VPS)

**Success Metrics:**
- Admins update status minimum 2x/day
- View → booking conversion: 10-15%
- 15-20+ businesses onboarded in Tyumen

## User Personas

### 1. Clients (Mobile/Web)
- Browse services on 2GIS map with real-time availability
- See wait times instead of "overloaded" status
- Online booking
- Filter by price, services, promotions
- Favorites and notifications
- Discount incentive for indicating "came through app"

### 2. Business Administrators (Desktop/PC)
- Admin panel with real-time data updates
- Update availability status (with sound/visual reminders)
- Manage bookings from the app
- Publish services, prices, promotions
- Track effectiveness metrics (views, bookings through app)

## Core Technical Decisions

### 2GIS Integration
- API documentation: https://dev.2gis.ru/en/api
- Used for map display and service location database
- Visual markers indicating availability (green = low load, with estimated wait time)

### Platform Architecture
- **Client apps**: Web (PWA recommended for MVP) + Mobile (iOS/Android for Phase 2)
- **Admin apps**: Desktop (Electron.js) or Web application
- **Real-time updates**: WebSocket or Server-Sent Events for availability status

### Known Challenges & Solutions

1. **Admin discipline (updating status)**
   - Onboarding with business owner
   - Sound/visual reminders in app

2. **Reluctance to show high load**
   - Display "approximate wait time 30 min" instead of "overloaded"
   - Positive framing

3. **Tracking app effectiveness**
   - Prompt clients for "came through app" with discount incentive
   - Analytics dashboard showing views → bookings conversion
   - Weekly email reports to business owners

## MVP Strategy (Tyumen Launch)

**Phase 1 Goals:**
- Onboard 15-20+ services in each category (car wash, repair)
- 3-month free trial period
- Build service density before client acquisition

**Phase 2 Goals:**
- Launch client acquisition campaigns
- Validate retention after free trial ends
- Expand to other cities via online marketing

**Success Metrics:**
- Admin status update frequency: minimum 2x/day
- View → booking conversion: target 10-15%
- Retention after trial: target 40%+

## Development Priorities

### MVP (Phase 1)
1. Web application for clients
2. Admin panel (desktop/web)
3. 2GIS map integration
4. Basic booking system
5. Admin reminder/notification system

### Post-MVP (Phase 2)
1. Mobile apps (iOS/Android)
2. Push notifications
3. Promo code system
4. Business analytics dashboard

## Technology Stack

### Backend
- **FastAPI 0.110+** (Python 3.11+) with **uv** package manager
- PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- Redis 7+ for caching
- WebSocket for real-time updates
- JWT authentication

### Frontend
- **Quasar Framework 2.x** (Vue 3 + PWA)
- Pinia for state management
- 2GIS Maps API 3.0 integration
- Axios for HTTP requests

### Hosting
- **Timeweb Cloud VPS** (Ubuntu 22.04)
  - Тариф: Cloud VPS Start (2GB RAM, 1 vCPU, 20GB SSD)
  - Цена: ~500₽/мес
  - URL: https://timeweb.cloud/
- Nginx reverse proxy
- SSL via Let's Encrypt (бесплатно)
- Домены: хичхайк.рф, api.хичхайк.рф, admin.хичхайк.рф

## Development Commands

### Backend (FastAPI)
```bash
# Setup
cd backend
uv venv && .venv\Scripts\activate  # Windows
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your settings (especially SECRET_KEY and DGIS_API_KEY)

# Database (using Docker)
cd ..
docker-compose up -d  # Start PostgreSQL and Redis

# Development
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000  # Run dev server

# Database migrations (if needed)
# Note: Manual migration already applied. For new migrations:
alembic revision --autogenerate -m "description"
alembic upgrade head

# Testing
pytest  # Run tests (when implemented)

# Code quality
ruff check .   # Lint
black .        # Format
```

**Important Notes:**
- Database schema is already created via manual migration in `alembic/versions/20251129_1220_initial_migration.py`
- If you encounter asyncpg connection issues on Windows, the database can be managed directly via Docker exec
- API documentation available at: http://localhost:8000/docs

### Frontend (Quasar)

**Admin Panel** (running on http://localhost:9001):
```bash
# Setup
cd admin-app
npm install

# Development
npm run dev                            # Run dev server (default: http://localhost:9001)

# Build
quasar build -m pwa                    # Build for production

# Code quality
npm run lint                           # Lint
npm run format                         # Format
```

**Client PWA** (to be implemented):
```bash
# Setup
cd client-app
npm install

# Development
quasar dev -m pwa                      # Run dev server (PWA mode)
quasar dev                             # Run dev server (SPA mode, faster)

# Build
quasar build -m pwa                    # Build for production
```

### Database
```bash
createdb hitchhike_db                  # Create database
psql hitchhike_db                      # Connect to database
```

## Project Structure

```
hitchhike/
├── backend/              # FastAPI application (http://localhost:8000)
│   ├── app/
│   │   ├── api/v1/      # API endpoints (auth, admin, client)
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── core/        # Core utilities (auth, DB, config)
│   ├── alembic/         # Database migrations
│   └── tests/           # Tests (to be implemented)
│
├── admin-app/           # ✅ Quasar Admin Panel (http://localhost:9001)
│   ├── src/
│   │   ├── pages/       # Vue pages (Login, Dashboard, Status, etc.)
│   │   ├── layouts/     # MainLayout with navigation
│   │   ├── stores/      # Pinia stores (auth)
│   │   ├── boot/        # Axios configuration with JWT
│   │   ├── router/      # Vue Router with auth guards
│   │   └── css/         # Styles (Tilda Sans fonts)
│   ├── public/fonts/    # Tilda Sans font files
│   └── quasar.config.js # Quasar configuration
│
├── client-app/          # 🔄 Quasar PWA (to be implemented)
│   └── (similar structure to admin-app)
│
├── fonts/               # Source font files (Tilda Sans)
│
└── docs/
    ├── dev_concept.md   # Business concept (Russian)
    ├── dev_plan.md      # Development plan (Russian)
    └── api_endpoints.md # API documentation
```

See **docs/dev_plan.md** for detailed technical stack, architecture, and development workflow.

## Key Implementation Notes

**Admin Panel (admin-app/):**
- **Framework:** Quasar 2.x with Vue 3 Composition API
- **Authentication:** JWT with automatic token refresh via Axios interceptors
- **State Management:** Pinia store for auth state
- **Routing:** Protected routes with navigation guards (requires Pinia initialized first)
- **Fonts:** Tilda Sans with all weight variations (Light to Black + Variable Font)
- **Development Server:** http://localhost:9001
- **Key Pages:**
  - LoginPage - JWT authentication
  - DashboardPage - Quick actions and overview
  - StatusPage - PRIMARY FEATURE for updating business availability
  - Services/Bookings/Promotions/Analytics/Profile - Placeholder pages

**2GIS Maps Integration (to be implemented in client-app):**
- Frontend: 2GIS JavaScript API 3.0 (`@2gis/mapgl`)
- Custom markers: 👍 thumbs up icon with color-coded availability
- Color scheme: Green (available), Yellow (busy), Orange (very busy)

**Real-time Updates (to be implemented):**
- FastAPI WebSocket endpoints for status updates
- Client subscribes to business status changes
- Admin receives notifications for new bookings

**PWA Features:**
- Installable on mobile devices (хичхайк.рф)
- Offline support via service workers
- Push notifications capability

**Authentication:**
- JWT tokens (access + refresh)
- Separate auth flows for clients and business admins
- Password hashing with argon2 (more secure and compatible than bcrypt)
- Token storage in localStorage
- Automatic refresh on 401 errors

## Environment Variables

Backend requires `.env` file (created from `.env.example`):
```bash
# Database (use 127.0.0.1 instead of localhost on Windows)
# Note: Docker PostgreSQL runs on port 5433 to avoid conflict with local PostgreSQL 17
DATABASE_URL=postgresql+asyncpg://hitchhike:hitchhike@127.0.0.1:5433/hitchhike_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT - IMPORTANT: Generate a secure key!
# Use: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secure-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 2GIS API
DGIS_API_KEY=your-2gis-api-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:9000,http://localhost:9001,http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Security Note**: Never commit `.env` file to Git. Always generate a new SECRET_KEY for production.

## Language Notes

- Primary documentation: Russian (docs/dev_concept.md, docs/dev_plan.md)
- Code and comments: English recommended
- UI for Russian market: Russian language
- Database/API naming: English conventions
