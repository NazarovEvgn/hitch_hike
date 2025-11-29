# ХичХайк (HitchHike)

Real-Time Service Availability Platform for auto service businesses integrated with 2GIS maps.

## 🎯 Project Overview

**ХичХайк** helps clients find available auto services (car washes, repair shops, tire services) in real-time and allows online booking. Businesses can update their availability status and manage bookings through an admin panel.

**Target Market:** Tyumen, Russia (MVP) → expansion to other cities

## 🏗️ Architecture

- **Backend:** FastAPI (Python 3.11+) with PostgreSQL and Redis
- **Client App:** Quasar Framework (Vue 3 PWA)
- **Admin App:** Quasar Framework (Vue 3 PWA)
- **Maps:** 2GIS Maps API 3.0

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+
- Docker & Docker Compose (recommended)
- uv package manager

### Backend Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Setup backend
cd backend
uv venv && .venv\Scripts\activate  # Windows
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

Server will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend Setup (Coming Soon)

```bash
# Client App
cd client-app
npm install
quasar dev

# Admin App
cd admin-app
npm install
quasar dev
```

## 📚 Documentation

- [Development Concept](docs/dev_concept.md) - Business concept and strategy (Russian)
- [Development Plan](docs/dev_plan.md) - Technical roadmap and architecture (Russian)
- [Map Integration](docs/map_integration.md) - 2GIS integration guide (Russian)
- [CLAUDE.md](CLAUDE.md) - AI assistant guidelines

## 🌟 Features

### For Clients
- 🗺️ Real-time availability map with color-coded markers (👍 green/yellow/orange)
- 📝 Online booking (no registration required for MVP)
- 🔍 Filter by service type and price
- 📞 Direct call and navigation to 2GIS

### For Business Admins
- 🟢 Update availability status (green/yellow/orange)
- 📅 Manage online bookings
- 💼 Publish services and promotions
- 📊 View analytics and conversion metrics

## 🔧 Technology Stack

**Backend:**
- FastAPI 0.110+ with uv package manager
- PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- Redis 7+ for caching
- JWT authentication
- WebSocket for real-time updates
- Alembic for migrations

**Frontend:**
- Quasar Framework 2.x
- Vue 3 (Composition API)
- Pinia state management
- 2GIS Maps API 3.0

**DevOps:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt SSL
- Timeweb Cloud VPS (~500₽/month)

## 📋 Current Status

✅ **Phase 1 - Backend Infrastructure (In Progress)**
- ✅ Project structure created
- ✅ Database models implemented
- ✅ Auth system (JWT) implemented
- ✅ Docker Compose configured
- ⏳ Database migrations
- ⏳ API endpoints implementation
- ⏳ WebSocket for real-time updates

🔜 **Phase 2 - Admin Panel**

🔜 **Phase 3 - Client App**

## 📝 API Endpoints

### Auth
- `POST /api/v1/auth/register/client` - Register client user
- `POST /api/v1/auth/register/business` - Register business with admin
- `POST /api/v1/auth/login/client` - Client login
- `POST /api/v1/auth/login/business` - Business admin login

### Health
- `GET /` - API info
- `GET /health` - Health check

Full API documentation: http://localhost:8000/docs

## 🎨 Brand Identity

**Logo:** 👍 Thumbs up icon with color-coded availability:
- 🟢 Green = available (0-15 min wait)
- 🟡 Yellow = busy (15-30 min wait)
- 🟠 Orange = very busy (30+ min wait)

**Domains:**
- хичхайк.рф (client PWA)
- api.хичхайк.рф (backend API)
- admin.хичхайк.рф (admin panel)

## 📝 License

Proprietary - All rights reserved

## 👤 Author

Evgeny Nazarov
- GitHub: [@NazarovEvgn](https://github.com/NazarovEvgn)

---

🚀 Built with FastAPI, Vue 3, and 2GIS Maps API
