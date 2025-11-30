# Быстрый старт для разработки

Инструкции по запуску всех компонентов системы ХичХайк.

---

## Предварительные требования

### Установленное ПО:
- **Python 3.11+** с менеджером пакетов `uv`
- **Node.js 16+** и **npm 8+**
- **Docker Desktop** (для PostgreSQL и Redis)
- **Git**

### Порты (должны быть свободны):
- `5433` - PostgreSQL
- `6379` - Redis
- `8000` - Backend API
- `9002` - Admin Panel
- `9000/9003` - Client PWA

### API ключи:
- **2GIS API Key** - для работы карты в клиентском приложении

---

## 0. Получение 2GIS API ключа (ВАЖНО!)

Клиентское приложение использует 2GIS MapGL для отображения карты. Для работы карты необходим API ключ.

### Шаги получения ключа:

1. **Регистрация на платформе 2GIS:**
   - Перейдите на https://dev.2gis.ru
   - Нажмите "Войти" или "Зарегистрироваться"
   - Заполните регистрационную форму

2. **Создание демо-ключа (бесплатно):**
   - После входа откройте Platform Manager
   - Создайте новый проект или используйте существующий
   - Выберите "Создать демо-ключ" (бесплатно для тестирования)
   - **Для студентов/некоммерческих проектов:** Выберите соответствующую категорию при создании ключа для расширенного бесплатного доступа

3. **Скопируйте полученный API ключ**

4. **Добавьте ключ в проект:**

```bash
# Откройте файл client-app/.env
# Замените 'your-2gis-api-key-here' на ваш реальный ключ
DGIS_API_KEY=ваш-настоящий-ключ-от-2gis
```

**Важно:**
- Без API ключа карта не будет загружаться (ошибка 400)
- Демо-ключ подходит для разработки и тестирования
- Для production потребуется коммерческая подписка

**Полезные ссылки:**
- Документация: https://docs.2gis.com/en/mapgl/overview
- Регистрация: https://dev.2gis.ru
- Примеры кода: https://www.npmjs.com/package/@2gis/mapgl

---

## 1. Запуск инфраструктуры (PostgreSQL + Redis)

### Первый запуск:

```bash
# Запуск Docker контейнеров
docker-compose up -d

# Проверка статуса
docker-compose ps
```

**Ожидаемый результат:**
```
NAME                      STATUS              PORTS
hitchhike-postgres-1      running             0.0.0.0:5433->5432/tcp
hitchhike-redis-1         running             0.0.0.0:6379->6379/tcp
```

### Остановка:

```bash
docker-compose down
```

### Полная очистка (удаление данных):

```bash
docker-compose down -v
```

---

## 2. Запуск Backend API

### Первичная настройка:

```bash
# Переход в директорию backend
cd backend

# Создание виртуального окружения (только первый раз)
uv venv

# Активация виртуального окружения
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Установка зависимостей (только первый раз)
uv pip install -e .

# Копирование и настройка .env (только первый раз)
cp .env.example .env
# Отредактируйте .env и добавьте SECRET_KEY
```

### Генерация SECRET_KEY для .env:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Запуск сервера:

```bash
# Из директории backend с активированным venv
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**URL:** http://127.0.0.1:8000
**API Docs:** http://127.0.0.1:8000/docs

### Проверка работы:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Ожидаемый ответ:
```json
{"status": "healthy"}
```

---

## 3. Запуск Admin Panel (Админ-панель для бизнесов)

### Первичная настройка:

```bash
# Переход в директорию admin-app
cd admin-app

# Установка зависимостей (только первый раз)
npm install
```

### Запуск dev-сервера:

```bash
npm run dev
```

**URL:** http://localhost:9002

### Тестовый аккаунт:
- **Email:** admin@testcarwash.ru
- **Пароль:** Test123456

### Сборка для production:

```bash
npm run build
```

---

## 4. Запуск Client PWA (Клиентское приложение)

### Первичная настройка:

```bash
# Переход в директорию client-app
cd client-app

# Установка зависимостей (только первый раз)
npm install
```

### Запуск dev-сервера:

```bash
npm run dev
```

**URL:** http://localhost:9000 (или http://localhost:9003 если порт занят)

### Сборка PWA для production:

```bash
npm run build
```

---

## Полный запуск всей системы

### Вариант 1: Вручную (несколько терминалов)

**Терминал 1: Инфраструктура**
```bash
docker-compose up -d
```

**Терминал 2: Backend**
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Терминал 3: Admin Panel**
```bash
cd admin-app
npm run dev
```

**Терминал 4: Client PWA**
```bash
cd client-app
npm run dev
```

---

## Проверка работы всех компонентов

### Backend API:
```bash
curl http://127.0.0.1:8000/api/v1/health
```

### PostgreSQL:
```bash
docker exec -it hitchhike-postgres-1 psql -U hitchhike -d hitchhike_db -c "SELECT version();"
```

### Redis:
```bash
docker exec -it hitchhike-redis-1 redis-cli ping
```

### Admin Panel:
Откройте http://localhost:9002 и войдите с тестовыми данными.

### Client PWA:
Откройте http://localhost:9000 (или порт, указанный при запуске).

---

## Полезные команды для разработки

### Backend:

```bash
# Создание новой миграции
cd backend
alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Проверка стиля кода
ruff check .

# Форматирование кода
black .
```

### Frontend (Admin & Client):

```bash
# Линтинг
npm run lint

# Форматирование
npm run format

# Очистка node_modules и переустановка
rm -rf node_modules package-lock.json
npm install
```

---

## Остановка всех компонентов

1. **Backend, Admin, Client**: Нажмите `Ctrl+C` в каждом терминале
2. **Docker**: `docker-compose down`

---

## Переменные окружения

### Backend (.env):

```env
# Database
DATABASE_URL=postgresql+asyncpg://hitchhike:hitchhike@127.0.0.1:5433/hitchhike_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=<сгенерированный-ключ>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 2GIS API
DGIS_API_KEY=your-2gis-api-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:9000,http://localhost:9001,http://localhost:9002,http://localhost:9003,http://localhost:3000

# Environment
ENVIRONMENT=development
```

---

## Работа с Git ветками

### Текущая структура:

- **main** - стабильная версия
- **feature/2gis-map-integration** - интеграция 2GIS карты (текущая)

### Переключение между ветками:

```bash
# Просмотр текущей ветки
git branch

# Переключение на main
git checkout main

# Переключение на ветку с картой
git checkout feature/2gis-map-integration

# Создание новой ветки
git checkout -b feature/my-new-feature
```

---

## Troubleshooting (Решение проблем)

### Порт уже занят:

```bash
# Windows: найти процесс на порту
netstat -ano | findstr :8000

# Убить процесс (замените PID на ID процесса)
taskkill /F /PID <PID>
```

### PostgreSQL не запускается (порт 5432 занят):

Проект настроен на порт **5433**, чтобы избежать конфликта с локальной установкой PostgreSQL.

### Backend не подключается к БД:

1. Проверьте что Docker контейнеры запущены: `docker-compose ps`
2. Проверьте DATABASE_URL в `.env`
3. Используйте `127.0.0.1` вместо `localhost` на Windows

### Admin/Client не запускается:

```bash
# Очистка node_modules
rm -rf node_modules package-lock.json
npm install

# Очистка кеша Quasar
rm -rf .quasar
```

### CORS ошибки:

Убедитесь что в `backend/.env` добавлен порт клиентского приложения в ALLOWED_ORIGINS.

---

## Дополнительная информация

- **Документация API:** http://127.0.0.1:8000/docs (Swagger UI)
- **Детальный план разработки:** `docs/dev_plan.md`
- **Концепция проекта:** `docs/dev_concept.md`
- **API endpoints:** `docs/api_endpoints.md`

---

**Дата создания:** 30 ноября 2025
**Версия:** Phase 4 (Client PWA в разработке)
