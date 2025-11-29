# План разработки MVP

## Цели MVP

**Главная цель**: Запустить функционирующее приложение в Тюмени с минимальным набором функций для валидации бизнес-модели.

**Критерии успеха MVP**:
- 15-20+ автосервисов подключены и активно используют админку
- Администраторы обновляют статус минимум 2 раза в день
- Клиенты могут видеть загруженность на карте и записываться онлайн
- Конверсия просмотр → запись: 10-15%
- Техническая стабильность: 99% uptime

## Архитектура системы

### Общая схема

```
[Client Web App (PWA)] ←→ [API Gateway] ←→ [Backend Services]
                                              ├─ Auth Service
                                              ├─ Booking Service
                                              ├─ Business Service
                                              ├─ Notification Service
                                              └─ Analytics Service
[Admin Web/Desktop] ←→ [API Gateway] ←→ [Backend Services]

[Backend] ←→ [PostgreSQL]
          ←→ [Redis Cache]
          ←→ [2GIS API]
          ←→ [SMS Provider (optional)]
```

### Технологический стек

**Backend:**
- **Framework**: FastAPI 0.110+ (Python 3.11+)
- **Package Manager**: uv (быстрый менеджер пакетов от Astral)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+ (async) + Alembic (миграции)
- **Cache**: Redis 7+
- **Real-time**: FastAPI WebSocket (нативная поддержка)
- **Auth**: JWT токены (python-jose + passlib)
- **Validation**: Pydantic V2
- **ASGI Server**: Uvicorn
- **Logging**: Loguru

**Frontend (Client App + Admin Panel):**
- **Framework**: Quasar Framework 2.x
  - Vue 3.4+ (Composition API)
  - Vite 5+ (сборщик)
- **State Management**: Pinia 2.x
- **UI Components**: Quasar Components (100+ компонентов)
- **Maps**: 2GIS JavaScript API 3.0
- **PWA**: Quasar PWA Mode + Workbox
- **HTTP Client**: Axios 1.6+
- **Real-time**: Native WebSocket API
- **Forms**: VeeValidate 4.x + Yup
- **Icons**: Material Icons (встроены в Quasar)
- **Utils**: VueUse 10.x

**Интеграции:**
- **2GIS API**: JavaScript API 3.0 (frontend) + REST API (backend)
- **Платежи**: ЮKassa или CloudPayments (Phase 2)
- **Email/SMS**: SMTP (Yandex Mail) или SendGrid (опционально)

**DevOps & Hosting:**
- **Hosting**: Timeweb Cloud VPS ⭐
  - Тариф: Cloud VPS Start (2GB RAM, 1 vCPU, 20GB SSD)
  - Цена: ~500₽/мес
  - ДатаЦентр: Москва или Санкт-Петербург
  - URL: https://timeweb.cloud/
- **OS**: Ubuntu 22.04 LTS
- **Web Server**: Nginx (reverse proxy + SSL)
- **SSL**: Let's Encrypt (Certbot) - бесплатно
- **Process Manager**: Systemd (для FastAPI)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (мониторинг ошибок)
- **Logs**: Loguru (Python) + journalctl
- **Backups**: pg_dump (PostgreSQL) через cron
- **Домены**:
  - хичхайк.рф (клиентское приложение)
  - api.хичхайк.рф (API backend)
  - admin.хичхайк.рф (админ панель)

## Структура базы данных

### Основные таблицы

```sql
-- Пользователи (клиенты)
users
  id, email, phone, name, password_hash, created_at, updated_at

-- Бизнесы (автосервисы)
businesses
  id, name, type (car_wash|repair_shop), address, lat, lon,
  phone, email, description, logo_url,
  2gis_id, subscription_status, subscription_end_date,
  created_at, updated_at

-- Администраторы бизнесов
business_admins
  id, business_id, email, password_hash, role, created_at

-- Услуги
services
  id, business_id, name, description, price, duration_minutes,
  is_active, created_at, updated_at

-- Статус загруженности (текущее состояние)
business_status
  id, business_id, status (available|busy|very_busy),
  estimated_wait_minutes, current_queue_count,
  updated_by_admin_id, updated_at

-- История статусов (для аналитики)
status_history
  id, business_id, status, estimated_wait_minutes,
  updated_at

-- Бронирования
bookings
  id, business_id, user_id, service_id,
  booking_date, booking_time, status (pending|confirmed|completed|cancelled),
  client_name, client_phone, notes,
  came_through_app (boolean),
  created_at, updated_at

-- Избранное
favorites
  id, user_id, business_id, created_at

-- Акции и скидки
promotions
  id, business_id, title, description, discount_percent,
  valid_from, valid_until, is_active, created_at

-- Уведомления администраторам
admin_reminders
  id, business_admin_id, reminder_type (update_status),
  sent_at, acknowledged_at

-- Аналитика просмотров
business_views
  id, business_id, user_id (nullable), view_date, source
```

## API Endpoints (REST)

### Auth
```
POST   /api/auth/register/client          # Регистрация клиента
POST   /api/auth/register/business        # Регистрация бизнеса
POST   /api/auth/login                    # Вход
POST   /api/auth/logout                   # Выход
POST   /api/auth/refresh                  # Обновление токена
```

### Client App
```
GET    /api/businesses                    # Список сервисов (фильтры, поиск)
GET    /api/businesses/:id                # Детали сервиса
GET    /api/businesses/:id/services       # Услуги сервиса
GET    /api/businesses/:id/promotions     # Акции сервиса
GET    /api/businesses/nearby             # Сервисы рядом (lat, lon)

POST   /api/bookings                      # Создать бронирование
GET    /api/bookings/my                   # Мои бронирования
PATCH  /api/bookings/:id/cancel           # Отменить бронирование

POST   /api/favorites                     # Добавить в избранное
DELETE /api/favorites/:id                 # Удалить из избранного
GET    /api/favorites/my                  # Мои избранные

POST   /api/analytics/view                # Зафиксировать просмотр сервиса
```

### Admin Panel
```
GET    /api/admin/business/profile        # Профиль бизнеса
PATCH  /api/admin/business/profile        # Обновить профиль

PATCH  /api/admin/status                  # Обновить статус загруженности
GET    /api/admin/status/history          # История обновлений статуса

GET    /api/admin/bookings                # Список бронирований
PATCH  /api/admin/bookings/:id            # Обновить статус бронирования

GET    /api/admin/services                # Список услуг
POST   /api/admin/services                # Создать услугу
PATCH  /api/admin/services/:id            # Обновить услугу
DELETE /api/admin/services/:id            # Удалить услугу

GET    /api/admin/promotions              # Список акций
POST   /api/admin/promotions              # Создать акцию
PATCH  /api/admin/promotions/:id          # Обновить акцию
DELETE /api/admin/promotions/:id          # Удалить акцию

GET    /api/admin/analytics               # Статистика (просмотры, бронирования)
GET    /api/admin/reminders               # Список напоминаний
PATCH  /api/admin/reminders/:id/ack       # Подтвердить напоминание
```

### WebSocket Events
```
# Client подписка
subscribe:business_status { business_ids: [] }
unsubscribe:business_status { business_ids: [] }

# Server → Client
business_status_updated { business_id, status, estimated_wait_minutes }

# Admin подписка
subscribe:admin_updates {}

# Server → Admin
new_booking { booking_data }
status_reminder { message }
```

## Интеграция с 2GIS API

### Необходимые endpoints 2GIS:
```
# Поиск организаций по типу
GET https://catalog.api.2gis.com/3.0/items
  ?q=автомойка&key=API_KEY&region_id=TYUMEN_ID

# Геокодирование адреса
GET https://catalog.api.2gis.com/3.0/items/geocode
  ?q=ADDRESS&key=API_KEY

# Построение маршрута
GET https://routing.api.2gis.com/...
```

### План интеграции:
1. Получить API ключ на https://dev.2gis.ru
2. Импортировать начальную базу автосервисов Тюмени из 2GIS
3. Хранить 2gis_id для синхронизации данных
4. Обновлять информацию раз в неделю (адреса, телефоны)
5. Использовать 2GIS карты на frontend

## Этапы разработки

### Этап 1: Инфраструктура и базовый backend (неделя 1-2)

**Задачи:**
- [ ] Настроить репозиторий (Git, структура папок)
- [ ] Поднять PostgreSQL + Redis (локально и на сервере)
- [ ] Создать базовую структуру backend проекта
- [ ] Реализовать миграции БД (все таблицы)
- [ ] Настроить Docker Compose для разработки
- [ ] Реализовать Auth систему (JWT, регистрация, вход)
- [ ] Настроить базовую CI/CD pipeline

**Результат:** Backend запущен, БД создана, можно регистрироваться и логиниться

### Этап 2: Admin Panel - базовый функционал (неделя 2-3)

**Задачи:**
- [ ] Создать Vue проект для админки
- [ ] Страница входа для администратора
- [ ] Дашборд с основной информацией
- [ ] Страница управления профилем бизнеса
- [ ] **Обновление статуса загруженности** (главная фича!)
  - [ ] Простой UI: выбор статуса + ввод времени ожидания
  - [ ] Реализовать API endpoint
  - [ ] WebSocket для real-time обновлений
- [ ] Список бронирований (пока пустой)
- [ ] Система напоминаний:
  - [ ] Cron job проверяет последнее обновление статуса
  - [ ] Если > 4 часов → звуковое уведомление в админке
  - [ ] Визуальный индикатор "обновите статус"

**Результат:** Администратор может войти и обновлять статус загруженности

### Этап 3: Client App - карта и просмотр сервисов (неделя 3-4)

**Задачи:**
- [ ] Создать React/Vue PWA проект
- [ ] Интегрировать 2GIS карты
- [ ] Получить API ключ 2GIS
- [ ] Импортировать тестовые данные автосервисов Тюмени
- [ ] Отобразить сервисы на карте с маркерами
- [ ] Цветовое кодирование маркеров:
  - Зеленый: доступен (0-15 мин ожидания)
  - Желтый: занят (15-30 мин)
  - Оранжевый: очень занят (30+ мин)
- [ ] Клик на маркер → карточка с информацией
- [ ] Страница детального просмотра сервиса
  - [ ] Информация о сервисе
  - [ ] Текущий статус и время ожидания
  - [ ] Список услуг с ценами
  - [ ] Кнопка "Записаться"
  - [ ] Кнопка "Построить маршрут" (через 2GIS)
- [ ] Фильтрация по типу сервиса (автомойка/СТО)
- [ ] Поиск по названию

**Результат:** Клиенты видят сервисы на карте с актуальной загруженностью

### Этап 4: Система бронирования (неделя 4-5)

**Задачи:**
- [ ] Client App: форма записи
  - [ ] Выбор услуги
  - [ ] Выбор даты и времени
  - [ ] Ввод контактных данных
  - [ ] Чекбокс "Пришел через приложение" (объяснить про скидку)
- [ ] Backend: создание бронирования
- [ ] Admin Panel: просмотр бронирований
  - [ ] Список всех записей
  - [ ] Фильтр по дате, статусу
  - [ ] Изменение статуса (подтвердить/отменить/завершить)
  - [ ] Уведомление при новой записи (WebSocket)
- [ ] Уведомления клиенту (опционально для MVP):
  - [ ] Email подтверждение записи
  - [ ] SMS напоминание (за день до записи)

**Результат:** Полный цикл онлайн-записи работает

### Этап 5: Управление контентом (неделя 5-6)


**Задачи:**
- [ ] Admin Panel: управление услугами
  - [ ] CRUD операции
  - [ ] Указание цены, длительности
  - [ ] Вкл/выкл услуги
- [ ] Admin Panel: управление акциями
  - [ ] Создание акции с описанием и сроком действия
  - [ ] Публикация/скрытие
- [ ] Client App: отображение услуг и акций
  - [ ] Список услуг на странице сервиса
  - [ ] Акции в отдельной секции
  - [ ] Бейдж "Акция!" на карточке сервиса

**Результат:** Бизнес может публиковать свои услуги и акции

### Этап 6: Дополнительные фичи клиента (неделя 6-7)

**Задачи:**
- [ ] Регистрация и профиль клиента
- [ ] Избранное:
  - [ ] Добавление в избранное
  - [ ] Страница "Мои избранные"
- [ ] История записей клиента
- [ ] Фильтрация по цене
- [ ] Сортировка результатов (по расстоянию, по цене, по загруженности)

**Результат:** Клиенты получают персонализированный опыт

### Этап 7: Аналитика для бизнеса (неделя 7-8)

**Задачи:**
- [ ] Отслеживание просмотров профиля
- [ ] Dashboard для бизнеса:
  - [ ] Просмотры профиля (график по дням)
  - [ ] Количество записей через приложение
  - [ ] Конверсия просмотр → запись
  - [ ] Сколько клиентов указали "пришел через приложение"
- [ ] Еженедельный email-отчет владельцу
- [ ] Экспорт данных (CSV)

**Результат:** Бизнес видит ценность приложения в цифрах

### Этап 8: Подписка и платежи (неделя 8-9)

**Задачи:**
- [ ] Интеграция платежного шлюза (ЮKassa или CloudPayments)
- [ ] Страница выбора тарифа
- [ ] Логика бесплатного пробного периода (3 месяца)
- [ ] Уведомления за 2 недели до окончания пробного периода
- [ ] Блокировка функций после окончания подписки
- [ ] Страница продления подписки
- [ ] Admin endpoint для управления подписками (для support)

**Результат:** Монетизация работает

### Этап 9: Тестирование и оптимизация (неделя 9-10)

**Задачи:**
- [ ] Нагрузочное тестирование
- [ ] Оптимизация запросов к БД (индексы)
- [ ] Кэширование статических данных в Redis
- [ ] PWA оптимизация (offline режим, быстрая загрузка)
- [ ] Cross-browser тестирование
- [ ] Мобильная адаптивность
- [ ] Исправление багов
- [ ] Написание базовой документации

**Результат:** Стабильное приложение готово к запуску

### Этап 10: Подготовка к запуску (неделя 10-11)

**Задачи:**
- [ ] Финальное тестирование на продакшн окружении
- [ ] Настройка мониторинга и логирования
- [ ] Создание инструкции для администраторов сервисов
- [ ] Создание промо-материалов (лендинг, презентация)
- [ ] Подготовка support материалов (FAQ, видео-инструкции)
- [ ] Настройка бэкапов БД
- [ ] SSL сертификаты
- [ ] Домены (например: app.servicemap.ru, admin.servicemap.ru)

**Результат:** Готово к онбордингу первых клиентов

## Структура проекта (рекомендуемая)

```
project_x/
├── backend/
│   ├── src/
│   │   ├── config/          # Конфигурация
│   │   ├── controllers/     # API controllers
│   │   ├── models/          # DB models
│   │   ├── services/        # Business logic
│   │   ├── middlewares/     # Auth, validation, etc.
│   │   ├── routes/          # API routes
│   │   ├── utils/           # Helpers
│   │   ├── websocket/       # WebSocket handlers
│   │   └── app.js           # Express app
│   ├── migrations/          # DB migrations
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
│
├── client-app/              # React/Vue PWA для клиентов
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/           # State management
│   │   ├── services/        # API calls
│   │   ├── utils/
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── admin-app/               # React/Vue для админки
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docs/                    # Документация
│   ├── dev_concept.md
│   ├── dev_plan.md         # Этот файл
│   └── api.md              # API документация
│
├── docker-compose.yml       # Для локальной разработки
├── CLAUDE.md
└── README.md
```

## Чек-лист перед запуском MVP

### Технические требования
- [ ] Все основные user flows работают без багов
- [ ] Приложение адаптировано для мобильных устройств
- [ ] PWA работает (можно добавить на домашний экран)
- [ ] Real-time обновления статуса работают
- [ ] Система напоминаний администраторам работает
- [ ] Платежная система протестирована
- [ ] Monitoring настроен (Sentry для ошибок)
- [ ] Бэкапы БД настроены (ежедневно)
- [ ] SSL сертификаты установлены
- [ ] Производительность приемлемая (страницы грузятся < 3 сек)

### Контент и данные
- [ ] База автосервисов Тюмени импортирована (минимум 50 заведений)
- [ ] 2GIS интеграция работает корректно
- [ ] Тестовые данные очищены
- [ ] Юридические документы готовы (договор, политика конфиденциальности)

### Бизнес-процессы
- [ ] Инструкция для администраторов готова (текст + видео)
- [ ] Презентация для привлечения бизнесов готова
- [ ] Support процесс настроен (куда писать, кто отвечает)
- [ ] Промо-материалы для клиентов готовы
- [ ] Сценарий онбординга первых бизнесов готов

## Риски и митигация

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Ограничения 2GIS API | Средняя | Высокое | Изучить лимиты заранее, иметь fallback на собственные карты |
| Низкая дисциплина админов | Высокая | Высокое | Геймификация, push-напоминания, показывать статистику эффективности |
| Медленная загрузка карты | Средняя | Среднее | Оптимизация, кэширование, CDN |
| Проблемы с платежами | Низкая | Высокое | Тестировать платежи заранее, иметь запасной шлюз |
| Недостаток клиентов | Высокая | Высокое | Маркетинг, партнерства с авто-сообществами |
| Технический долг при быстрой разработке | Высокая | Среднее | Выделить время на рефакторинг после запуска |

## Следующие шаги после MVP

1. **Анализ метрик** (первые 3 месяца):
   - Retention администраторов после пробного периода
   - Активность обновления статусов
   - Конверсия в записи
   - Feedback от пользователей

2. **Улучшения на основе feedback**:
   - Приоритизация новых фич
   - Оптимизация UX

3. **Масштабирование**:
   - Мобильные приложения (iOS/Android)
   - Экспансия в другие города
   - Новые типы сервисов

4. **Дополнительные фичи**:
   - Программа лояльности
   - Интеграция с существующими CRM сервисов
   - Автоматический расчет загруженности по записям
   - Чат с сервисом
   - Отзывы и рейтинги