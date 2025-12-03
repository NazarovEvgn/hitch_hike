<template>
  <div class="full-height">
    <div id="map-container">
      <!-- Панель фильтров -->
      <div class="filter-panel q-pa-md">
        <div class="row q-gutter-sm">
          <q-btn
            :flat="selectedType !== 'car_wash'"
            :unelevated="selectedType === 'car_wash'"
            :color="selectedType === 'car_wash' ? 'primary' : 'grey-7'"
            icon="local_car_wash"
            label="Автомойки"
            @click="selectType('car_wash')"
          />
          <q-btn
            :flat="selectedType !== 'repair_shop'"
            :unelevated="selectedType === 'repair_shop'"
            :color="selectedType === 'repair_shop' ? 'primary' : 'grey-7'"
            icon="build"
            label="Ремонт"
            @click="selectType('repair_shop')"
          />
          <q-btn
            :flat="selectedType !== 'tire_service'"
            :unelevated="selectedType === 'tire_service'"
            :color="selectedType === 'tire_service' ? 'primary' : 'grey-7'"
            icon="album"
            label="Шиномонтаж"
            @click="selectType('tire_service')"
          />
          <q-space />
          <q-btn
            flat
            round
            dense
            icon="favorite"
            color="red"
            @click="$router.push('/favorites')"
          >
            <q-badge v-if="favoritesCount > 0" color="red" floating>{{ favoritesCount }}</q-badge>
          </q-btn>
        </div>
      </div>

      <!-- Контейнер для карты 2GIS -->
      <div ref="mapContainer" style="width: 100%; height: 100%"></div>

      <!-- Карточка бизнеса (показывается при клике на маркер) -->
      <div v-if="selectedBusiness" class="business-card">
        <q-card flat>
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">{{ selectedBusiness.name }}</div>
                <div class="text-caption text-grey-7">{{ businessTypeLabel(selectedBusiness.type) }}</div>
              </div>
              <q-btn flat round dense icon="close" @click="selectedBusiness = null" />
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="q-gutter-sm">
              <div class="row items-center">
                <q-icon name="schedule" class="q-mr-sm" />
                <span>{{ statusLabel(selectedBusiness.status?.status || 'available') }}</span>
                <q-chip
                  :color="statusColor(selectedBusiness.status?.status || 'available')"
                  text-color="white"
                  class="q-ml-sm"
                />
              </div>
              <div class="row items-center">
                <q-icon name="location_on" class="q-mr-sm" />
                <span>{{ selectedBusiness.address }}</span>
              </div>
              <div class="row items-center">
                <q-icon name="phone" class="q-mr-sm" />
                <span>{{ selectedBusiness.phone }}</span>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions class="q-pa-md">
            <q-btn
              unelevated
              color="primary"
              icon="phone"
              label="Позвонить"
              @click="call(selectedBusiness.phone)"
              class="col"
            />
            <q-btn
              unelevated
              color="secondary"
              icon="event"
              label="Записаться"
              @click="bookService(selectedBusiness)"
              class="col"
            />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Booking Dialog -->
    <BookingDialog
      v-model="showBookingDialog"
      :business="businessToBook"
      @booking-created="onBookingCreated"
    />
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'
import BookingDialog from 'components/BookingDialog.vue'

export default defineComponent({
  name: 'MapPage',

  components: {
    BookingDialog
  },

  setup() {
    const $q = useQuasar()
    const mapContainer = ref(null)
    const map = ref(null) // Экземпляр карты 2GIS
    const mapglAPI = ref(null) // API 2GIS MapGL
    const selectedType = ref(null)
    const selectedBusiness = ref(null)
    const favoritesCount = ref(0)
    const businesses = ref([]) // Список бизнесов
    const markers = ref([]) // Маркеры на карте

    // Booking dialog state
    const showBookingDialog = ref(false)
    const businessToBook = ref(null)

    const selectType = (type) => {
      if (selectedType.value === type) {
        selectedType.value = null
      } else {
        selectedType.value = type
      }
      filterMarkers()
    }

    const businessTypeLabel = (type) => {
      const labels = {
        car_wash: 'Автомойка',
        repair_shop: 'Автосервис',
        tire_service: 'Шиномонтаж'
      }
      return labels[type] || type
    }

    const statusLabel = (status) => {
      const labels = {
        available: 'Свободно (0-15 мин)',
        busy: 'Занято (15-30 мин)',
        very_busy: 'Очень загружены (30+ мин)'
      }
      return labels[status] || status
    }

    const statusColor = (status) => {
      const colors = {
        available: 'green',
        busy: 'orange',
        very_busy: 'red'
      }
      return colors[status] || 'grey'
    }

    const call = (phone) => {
      window.location.href = `tel:${phone}`
    }

    const bookService = (business) => {
      businessToBook.value = business
      showBookingDialog.value = true
    }

    const onBookingCreated = (booking) => {
      console.log('Booking created:', booking)
      // Refresh bookings or update UI if needed
    }

    // Загрузка бизнесов из API
    const loadBusinesses = async () => {
      try {
        const center = [65.5343, 57.1522] // Центр Тюмени
        const response = await api.get('/businesses/nearby', {
          params: {
            lat: center[1], // 2GIS использует [lon, lat], а API [lat, lon]
            lon: center[0],
            radius_km: 20
          }
        })
        businesses.value = response.data
        console.log('Loaded businesses:', businesses.value)
        createMarkers()
      } catch (error) {
        console.error('Failed to load businesses:', error)
        $q.notify({
          type: 'warning',
          message: 'Не удалось загрузить сервисы. Попробуйте позже.'
        })
      }
    }

    // Создание маркеров на карте
    const createMarkers = () => {
      if (!map.value || !mapglAPI.value) return

      // Удаляем старые маркеры
      markers.value.forEach(item => item.marker.destroy())
      markers.value = []

      // Создаем новые маркеры
      businesses.value.forEach(business => {
        console.log('Creating marker for:', business.name, 'at', [business.lon, business.lat], 'status:', business.status?.status)

        // Брендовые цвета
        const primaryColor = '#27126A' // Фиолетовый (основной)
        const accentColor = '#98EA14'  // Зеленый (акцентирующий)
        const isAvailable = business.status?.status === 'available'

        // Создаем HTML для маркера с индикатором доступности
        const markerHTML = `
          <div class="custom-marker" style="
            position: relative;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: ${primaryColor};
            box-shadow: 0 2px 8px rgba(0,0,0,0.5);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            user-select: none;
          " data-business-id="${business.id}">
            ${isAvailable ? `
              <div style="
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: ${accentColor};
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
              "></div>
            ` : ''}
          </div>
        `

        console.log('Creating marker for:', business.name, 'available:', isAvailable)

        try {
          const marker = new mapglAPI.value.HtmlMarker(map.value, {
            coordinates: [business.lon, business.lat],
            html: markerHTML
          })

          console.log('Marker created successfully')

          // Сохраняем маркер с информацией о бизнесе
          markers.value.push({
            marker,
            element: null, // Элемент получим через делегирование
            business
          })
        } catch (error) {
          console.error('Failed to create marker:', error)
        }
      })

      console.log(`Created ${markers.value.length} markers`)
    }

    // Фильтрация маркеров по типу
    const filterMarkers = () => {
      markers.value.forEach(item => {
        if (!selectedType.value || item.business.type === selectedType.value) {
          item.element.style.display = 'flex'
        } else {
          item.element.style.display = 'none'
        }
      })
    }

    const initMap = async () => {
      try {
        // Динамический импорт 2GIS MapGL
        const { load } = await import('@2gis/mapgl')
        mapglAPI.value = await load()

        // API ключ из переменных окружения
        const apiKey = process.env.DGIS_API_KEY || 'bc1703bf-053c-4f08-abed-a8817260c0e7'
        console.log('Using 2GIS API key:', apiKey.substring(0, 8) + '...')

        // Создание карты с центром на Тюмени
        map.value = new mapglAPI.value.Map(mapContainer.value, {
          center: [65.5343, 57.1522], // Координаты Тюмени [lon, lat]
          zoom: 12,
          key: apiKey
        })

        console.log('2GIS Map initialized successfully')

        // Добавляем обработчик кликов на карту для делегирования событий
        mapContainer.value.addEventListener('click', (e) => {
          const marker = e.target.closest('.custom-marker')
          if (marker) {
            const businessId = parseInt(marker.dataset.businessId)
            const business = businesses.value.find(b => b.id === businessId)
            if (business) {
              console.log('Marker clicked:', business.name)
              selectedBusiness.value = business
              map.value.setCenter([business.lon, business.lat])
            }
          }
        })

        // Загрузка бизнесов после инициализации карты
        await loadBusinesses()
      } catch (error) {
        console.error('Failed to initialize 2GIS map:', error)
        $q.notify({
          type: 'negative',
          message: 'Не удалось загрузить карту. Проверьте подключение к интернету.'
        })
      }
    }

    onMounted(() => {
      initMap()
    })

    onBeforeUnmount(() => {
      // Очистка маркеров при размонтировании
      markers.value.forEach(item => item.marker.destroy())
      markers.value = []
      if (map.value) {
        map.value.destroy()
      }
    })

    return {
      mapContainer,
      selectedType,
      selectedBusiness,
      favoritesCount,
      selectType,
      businessTypeLabel,
      statusLabel,
      statusColor,
      call,
      bookService,
      showBookingDialog,
      businessToBook,
      onBookingCreated
    }
  }
})
</script>
