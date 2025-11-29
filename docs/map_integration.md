# Интеграция карты 2GIS для ХичХайк

## Обзор

Этот документ описывает полную интеграцию 2GIS карты в проект ХичХайк с кастомными маркерами автосервисов.

---

## 📋 Требования

### Функциональные требования:
- ✅ Отображение карты Тюмени с автосервисами
- ✅ Кастомные маркеры 👍 с цветовой индикацией загруженности
- ✅ Фильтрация по типу сервиса (автомойка, СТО, шиномонтаж)
- ✅ Клик на маркер → карточка с информацией + 3 кнопки
- ✅ Real-time обновление статусов через WebSocket
- ✅ Построение маршрута (переход на 2GIS)

### Технические требования:
- 2GIS JavaScript API 3.0
- Vue 3 (Composition API)
- Quasar Framework
- Axios для API запросов
- WebSocket для real-time обновлений

---

## 🚀 Быстрый старт

### 1. Получение API ключа 2GIS

1. Зарегистрироваться на https://dev.2gis.ru/
2. Создать новый проект
3. Получить API ключ
4. Добавить в `.env`:
   ```bash
   VITE_DGIS_API_KEY=your-api-key-here
   ```

### 2. Установка зависимостей

```bash
npm install @2gis/mapgl
npm install @2gis/mapgl-clusterer  # Для кластеризации (опционально)
```

### 3. Базовая инициализация

```javascript
import { load } from '@2gis/mapgl';

const mapglAPI = await load();
const map = new mapglAPI.Map('map-container', {
  center: [65.534328, 57.152985], // Тюмень
  zoom: 13,
  key: import.meta.env.VITE_DGIS_API_KEY,
});
```

---

## 💻 Полная реализация MapView.vue

### Компонент карты (client-app/src/components/Map/MapView.vue)

```vue
<template>
  <div class="map-wrapper">
    <!-- Фильтры по типу сервиса -->
    <div class="filter-panel">
      <q-btn-group>
        <q-btn
          @click="filterByType(null)"
          :color="selectedType === null ? 'primary' : 'white'"
          label="Все"
        />
        <q-btn
          @click="filterByType('car_wash')"
          :color="selectedType === 'car_wash' ? 'primary' : 'white'"
          icon="local_car_wash"
          label="Автомойка"
        />
        <q-btn
          @click="filterByType('repair_shop')"
          :color="selectedType === 'repair_shop' ? 'primary' : 'white'"
          icon="build"
          label="СТО"
        />
        <q-btn
          @click="filterByType('tire_service')"
          :color="selectedType === 'tire_service' ? 'primary' : 'white'"
          icon="trip_origin"
          label="Шиномонтаж"
        />
      </q-btn-group>
    </div>

    <!-- Контейнер карты -->
    <div id="map-container" class="map-container"></div>

    <!-- Карточка бизнеса (попап) -->
    <q-dialog v-model="showBusinessCard" position="bottom">
      <BusinessCard
        :business="selectedBusiness"
        @book="openBookingForm"
        @call="callBusiness"
        @navigate="navigateToBusiness"
      />
    </q-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, onUnmounted } from 'vue';
import { load } from '@2gis/mapgl';
import { useBusinessStore } from 'src/stores/businesses';
import { useWebSocket } from 'src/composables/useWebSocket';
import BusinessCard from './BusinessCard.vue';

// Store
const businessStore = useBusinessStore();

// Refs
const map = ref(null);
const mapglAPI = ref(null);
const markers = ref([]);
const selectedType = ref(null);
const selectedBusiness = ref(null);
const showBusinessCard = ref(false);

// WebSocket для real-time обновлений
const { socket } = useWebSocket();

// Инициализация карты
onMounted(async () => {
  try {
    // Загружаем 2GIS API
    mapglAPI.value = await load();

    // Создаем карту (центр - Тюмень)
    map.value = new mapglAPI.value.Map('map-container', {
      center: [65.534328, 57.152985], // lon, lat Тюмени
      zoom: 13,
      key: import.meta.env.VITE_DGIS_API_KEY,
      style: '2gis://styles/default', // Стиль карты
    });

    // Добавляем контролы
    map.value.addControl(new mapglAPI.value.ZoomControl(), 'topRight');
    map.value.addControl(new mapglAPI.value.GeolocateControl(), 'topRight');

    // Загружаем автосервисы
    await loadBusinesses();

    // Подписываемся на WebSocket обновления
    subscribeToUpdates();

  } catch (error) {
    console.error('Ошибка инициализации карты:', error);
  }
});

// Очистка при размонтировании
onUnmounted(() => {
  clearMarkers();
  if (map.value) {
    map.value.destroy();
  }
});

// Загрузка автосервисов
async function loadBusinesses(type = null) {
  try {
    const businesses = await businessStore.fetchBusinesses(type);

    // Очищаем старые маркеры
    clearMarkers();

    // Добавляем новые маркеры
    businesses.forEach(business => {
      addCustomMarker(business);
    });

  } catch (error) {
    console.error('Ошибка загрузки автосервисов:', error);
  }
}

// Добавление кастомного маркера
function addCustomMarker(business) {
  // Создаем HTML элемент для маркера
  const el = document.createElement('div');
  el.className = 'custom-marker';
  el.style.cursor = 'pointer';

  // Определяем цвет маркера по статусу
  const markerColor = getMarkerColor(business.status);

  // Создаем иконку маркера (👍 большой палец)
  el.innerHTML = `
    <div style="
      position: relative;
      width: 50px;
      height: 50px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: ${markerColor};
      border-radius: 50%;
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      transition: transform 0.2s;
    ">
      <div style="font-size: 24px;">👍</div>
      ${business.estimated_wait_minutes > 0 ? `
        <div style="
          position: absolute;
          bottom: -8px;
          background: white;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          font-weight: bold;
          color: #333;
        ">${business.estimated_wait_minutes} мин</div>
      ` : ''}
    </div>
  `;

  // Hover эффект
  el.addEventListener('mouseenter', () => {
    el.firstElementChild.style.transform = 'scale(1.1)';
  });
  el.addEventListener('mouseleave', () => {
    el.firstElementChild.style.transform = 'scale(1)';
  });

  // Создаем маркер на карте
  const marker = new mapglAPI.value.HtmlMarker(map.value, {
    coordinates: [business.lon, business.lat],
    html: el,
  });

  // Обработка клика на маркер
  el.addEventListener('click', () => {
    selectedBusiness.value = business;
    showBusinessCard.value = true;

    // Центрируем карту на маркере
    map.value.setCenter([business.lon, business.lat]);
  });

  // Сохраняем маркер с ID бизнеса для обновлений
  markers.value.push({
    id: business.id,
    marker: marker,
    element: el,
  });
}

// Определение цвета маркера по статусу
function getMarkerColor(status) {
  const colors = {
    available: '#10B981',     // 🟢 Зеленый
    busy: '#F59E0B',          // 🟡 Желтый
    very_busy: '#F97316',     // 🟠 Оранжевый
  };
  return colors[status] || '#10B981';
}

// Очистка всех маркеров
function clearMarkers() {
  markers.value.forEach(({ marker }) => {
    marker.destroy();
  });
  markers.value = [];
}

// Фильтрация по типу сервиса
async function filterByType(type) {
  selectedType.value = type;
  await loadBusinesses(type);
}

// Подписка на WebSocket обновления статусов
function subscribeToUpdates() {
  if (!socket.value) return;

  socket.value.on('business_status_updated', (data) => {
    // data = { business_id, status, estimated_wait_minutes }
    updateMarkerStatus(data);
  });
}

// Обновление статуса маркера
function updateMarkerStatus(data) {
  const markerObj = markers.value.find(m => m.id === data.business_id);
  if (!markerObj) return;

  const newColor = getMarkerColor(data.status);

  // Обновляем цвет маркера
  const markerDiv = markerObj.element.firstElementChild;
  markerDiv.style.background = newColor;

  // Обновляем время ожидания
  const timeLabel = markerDiv.querySelector('div[style*="position: absolute"]');
  if (data.estimated_wait_minutes > 0) {
    if (timeLabel) {
      timeLabel.textContent = `${data.estimated_wait_minutes} мин`;
    } else {
      markerDiv.innerHTML += `
        <div style="
          position: absolute;
          bottom: -8px;
          background: white;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          font-weight: bold;
          color: #333;
        ">${data.estimated_wait_minutes} мин</div>
      `;
    }
  } else if (timeLabel) {
    timeLabel.remove();
  }
}

// Открыть форму бронирования
function openBookingForm(business) {
  // Переход на страницу бронирования или открытие модалки
  // router.push(`/booking/${business.id}`);
}

// Позвонить в сервис
function callBusiness(business) {
  window.location.href = `tel:${business.phone}`;
}

// Построить маршрут в 2GIS
function navigateToBusiness(business) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;

        // URL для открытия маршрута в 2GIS
        const routeUrl = `https://2gis.ru/routeSearch/rsType/car/from/${userLon},${userLat}/to/${business.lon},${business.lat}`;

        // Открываем в новой вкладке
        window.open(routeUrl, '_blank');
      },
      (error) => {
        console.error('Геолокация недоступна:', error);
        // Открываем 2GIS без начальной точки
        const routeUrl = `https://2gis.ru/tyumen/firm/${business.dgis_id || business.id}`;
        window.open(routeUrl, '_blank');
      }
    );
  } else {
    // Браузер не поддерживает геолокацию
    const routeUrl = `https://2gis.ru/tyumen/firm/${business.dgis_id || business.id}`;
    window.open(routeUrl, '_blank');
  }
}
</script>

<style lang="scss" scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
}

.filter-panel {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.map-container {
  width: 100%;
  height: 100%;
}

.custom-marker {
  transition: transform 0.2s;
}
</style>
```

---

## 📱 Компонент карточки бизнеса

### BusinessCard.vue

```vue
<template>
  <q-card class="business-card">
    <q-card-section>
      <div class="text-h6">{{ business.name }}</div>
      <div class="text-subtitle2 text-grey-7">{{ business.address }}</div>
    </q-card-section>

    <q-card-section>
      <!-- Статус загруженности -->
      <div class="status-indicator">
        <q-chip
          :color="statusColor"
          text-color="white"
          icon="schedule"
        >
          {{ statusText }}
        </q-chip>
      </div>

      <!-- Услуги и цены (кратко) -->
      <div class="services-preview q-mt-md">
        <div v-for="service in business.services.slice(0, 3)" :key="service.id" class="service-item">
          <span>{{ service.name }}</span>
          <span class="text-weight-bold">{{ formatPrice(service.price_from, service.price_to) }}</span>
        </div>
        <div v-if="business.services.length > 3" class="text-caption text-grey-7">
          +{{ business.services.length - 3 }} услуг
        </div>
      </div>
    </q-card-section>

    <q-card-actions>
      <!-- 3 главные кнопки -->
      <q-btn
        flat
        color="primary"
        icon="phone"
        label="Позвонить"
        @click="emit('call', business)"
      />
      <q-btn
        flat
        color="primary"
        icon="event"
        label="Записаться"
        @click="emit('book', business)"
      />
      <q-btn
        flat
        color="primary"
        icon="directions"
        label="Маршрут"
        @click="emit('navigate', business)"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  business: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['call', 'book', 'navigate']);

const statusColor = computed(() => {
  const colors = {
    available: 'green',
    busy: 'orange',
    very_busy: 'deep-orange',
  };
  return colors[props.business.status] || 'green';
});

const statusText = computed(() => {
  const texts = {
    available: `Свободно${props.business.estimated_wait_minutes > 0 ? ` (${props.business.estimated_wait_minutes} мин)` : ''}`,
    busy: `Средняя загрузка (${props.business.estimated_wait_minutes} мин)`,
    very_busy: `Высокая загрузка (${props.business.estimated_wait_minutes} мин)`,
  };
  return texts[props.business.status] || 'Свободно';
});

function formatPrice(priceFrom, priceTo) {
  if (priceFrom && priceTo && priceFrom !== priceTo) {
    return `${priceFrom}-${priceTo} ₽`;
  } else if (priceFrom) {
    return `от ${priceFrom} ₽`;
  }
  return 'По запросу';
}
</script>

<style lang="scss" scoped>
.business-card {
  min-width: 300px;
}

.status-indicator {
  display: flex;
  align-items: center;
}

.services-preview {
  .service-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
  }
}
</style>
```

---

## 🔌 WebSocket для real-time обновлений

### composables/useWebSocket.js

```javascript
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

export function useWebSocket() {
  const socket = ref(null);
  const connected = ref(false);

  onMounted(() => {
    // Подключение к WebSocket серверу
    socket.value = io(import.meta.env.VITE_API_URL, {
      transports: ['websocket'],
    });

    socket.value.on('connect', () => {
      connected.value = true;
      console.log('WebSocket подключен');
    });

    socket.value.on('disconnect', () => {
      connected.value = false;
      console.log('WebSocket отключен');
    });
  });

  onUnmounted(() => {
    if (socket.value) {
      socket.value.disconnect();
    }
  });

  return {
    socket,
    connected,
  };
}
```

---

## 📊 Pinia Store для бизнесов

### stores/businesses.js

```javascript
import { defineStore } from 'pinia';
import axios from 'axios';

export const useBusinessStore = defineStore('businesses', {
  state: () => ({
    businesses: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchBusinesses(type = null) {
      this.loading = true;
      this.error = null;

      try {
        const params = type ? { type } : {};
        const response = await axios.get('/api/businesses', { params });

        this.businesses = response.data;
        return response.data;
      } catch (error) {
        this.error = error.message;
        console.error('Ошибка загрузки бизнесов:', error);
        return [];
      } finally {
        this.loading = false;
      }
    },

    updateBusinessStatus(businessId, status) {
      const business = this.businesses.find(b => b.id === businessId);
      if (business) {
        business.status = status.status;
        business.estimated_wait_minutes = status.estimated_wait_minutes;
      }
    },
  },
});
```

---

## 🎨 Варианты дизайна маркеров

### Вариант 1: Простой эмодзи
```javascript
el.innerHTML = `<span style="font-size: 32px; color: ${color};">👍</span>`;
```

### Вариант 2: С фоном и тенью
```javascript
el.innerHTML = `
  <div style="
    background: ${color};
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  ">
    <span style="font-size: 28px;">👍</span>
  </div>
`;
```

### Вариант 3: С временем ожидания (РЕКОМЕНДУЕТСЯ)
```javascript
el.innerHTML = `
  <div style="
    position: relative;
    background: ${color};
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  ">
    <div style="font-size: 24px;">👍</div>
    ${business.estimated_wait_minutes > 0 ? `
      <div style="
        position: absolute;
        bottom: -8px;
        background: white;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: bold;
        color: #333;
      ">${business.estimated_wait_minutes} мин</div>
    ` : ''}
  </div>
`;
```

---

## 🚀 Дополнительные возможности

### Кластеризация маркеров (для масштабирования)

```javascript
import { MarkerClusterer } from '@2gis/mapgl-clusterer';

const clusterer = new MarkerClusterer(map.value, {
  radius: 60,
  clusterStyle: {
    color: '#10B981',
    size: 50,
  },
});

// Добавляем маркеры в кластер
markers.value.forEach(({ marker }) => {
  clusterer.addMarker(marker);
});
```

### Геолокация пользователя

```javascript
// Добавляем кнопку геолокации
map.value.addControl(new mapglAPI.value.GeolocateControl(), 'topRight');

// Или программно
navigator.geolocation.getCurrentPosition((position) => {
  const userMarker = new mapglAPI.value.Marker(map.value, {
    coordinates: [position.coords.longitude, position.coords.latitude],
  });

  map.value.setCenter([position.coords.longitude, position.coords.latitude]);
  map.value.setZoom(15);
});
```

### Поиск ближайшего сервиса

```javascript
function findNearestBusiness(userLat, userLon, businesses) {
  return businesses
    .map(b => ({
      ...b,
      distance: calculateDistance(userLat, userLon, b.lat, b.lon)
    }))
    .sort((a, b) => a.distance - b.distance)[0];
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Радиус Земли в км
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Расстояние в км
}
```

---

## 📝 Чек-лист интеграции

### Backend:
- [ ] API endpoint `/api/businesses` возвращает список с координатами
- [ ] WebSocket endpoint для real-time обновлений статусов
- [ ] Поле `dgis_id` в БД для связки с 2GIS

### Frontend:
- [ ] Установлен `@2gis/mapgl`
- [ ] Получен API ключ 2GIS
- [ ] Компонент `MapView.vue` создан
- [ ] Компонент `BusinessCard.vue` создан
- [ ] Pinia store для бизнесов настроен
- [ ] WebSocket composable реализован
- [ ] Кастомные маркеры с цветовой индикацией работают
- [ ] Фильтрация по типу сервиса работает
- [ ] Клик на маркер открывает карточку
- [ ] Кнопки "Позвонить", "Записаться", "Маршрут" работают
- [ ] Real-time обновления статусов работают

### Тестирование:
- [ ] Карта загружается корректно
- [ ] Маркеры отображаются в правильных местах
- [ ] Цвета маркеров соответствуют статусам
- [ ] Фильтры работают
- [ ] WebSocket обновления работают
- [ ] Построение маршрута открывает 2GIS
- [ ] Мобильная версия работает корректно

---

## 🔗 Полезные ссылки

- [2GIS JavaScript API 3.0 Documentation](https://dev.2gis.ru/en/javascript/3.0/)
- [2GIS Examples](https://docs.2gis.com/en/mapgl/examples)
- [Quasar Framework](https://quasar.dev/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia Store](https://pinia.vuejs.org/)

---

## ⚠️ Важные замечания

1. **API ключ**: Никогда не коммитьте API ключ в Git. Используйте `.env` файлы.

2. **Производительность**: При большом количестве маркеров (100+) используйте кластеризацию.

3. **Геолокация**: Запрос геолокации требует HTTPS (кроме localhost).

4. **Мобильная оптимизация**: Тестируйте на реальных устройствах, размеры маркеров должны быть touch-friendly (минимум 44x44 px).

5. **Fallback**: Предусмотрите fallback если 2GIS API недоступен или браузер не поддерживает WebGL.

---

## 📞 Контакты для поддержки

- 2GIS Support: https://help.2gis.ru/
- 2GIS Developer Portal: https://dev.2gis.ru/
