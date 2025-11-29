# ХичХайк - Админ Панель

Админ-панель для управления автосервисами на платформе ХичХайк.

## Технологии

- **Quasar Framework 2.x** - Vue 3 + компоненты UI
- **Vue 3** - Composition API
- **Pinia** - управление состоянием
- **Vue Router** - роутинг
- **Axios** - HTTP клиент
- **Tilda Sans** - фирменный шрифт

## Установка зависимостей

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
# или
quasar dev
```

Приложение будет доступно по адресу http://localhost:9001

## Сборка для продакшена

```bash
npm run build
# или
quasar build
```

## Структура проекта

```
admin-app/
├── public/              # Статические файлы
│   └── fonts/          # Шрифты Tilda Sans
├── src/
│   ├── boot/           # Инициализация (axios)
│   ├── components/     # Vue компоненты
│   ├── css/            # Стили и шрифты
│   ├── layouts/        # Layouts (MainLayout)
│   ├── pages/          # Страницы приложения
│   ├── router/         # Vue Router конфигурация
│   ├── stores/         # Pinia stores
│   ├── App.vue         # Корневой компонент
│   └── main.js         # Точка входа
└── quasar.config.js    # Конфигурация Quasar
```

## Основные страницы

- `/login` - Вход в систему
- `/` - Главная панель (Dashboard)
- `/status` - Обновление статуса загруженности ⭐ PRIMARY FEATURE
- `/bookings` - Управление бронированиями
- `/services` - Управление услугами
- `/promotions` - Управление акциями
- `/analytics` - Аналитика
- `/profile` - Настройки профиля

## API Integration

Backend API: http://127.0.0.1:8000/api/v1

Настройка переменных окружения в `quasar.config.js`:
```javascript
env: {
  API_URL: process.env.API_URL || 'http://127.0.0.1:8000/api/v1'
}
```

## Аутентификация

Используется JWT токены (access + refresh). Токены сохраняются в localStorage.

## Разработка

Следуйте руководству в `CLAUDE.md` корневой директории проекта.
