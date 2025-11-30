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
                <span>{{ statusLabel(selectedBusiness.status) }}</span>
                <q-chip
                  :color="statusColor(selectedBusiness.status)"
                  text-color="white"
                  class="q-ml-sm"
                >
                  {{ selectedBusiness.status === 'available' ? '🟢' : selectedBusiness.status === 'busy' ? '🟡' : '🟠' }}
                </q-chip>
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
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'MapPage',

  setup() {
    const $q = useQuasar()
    const mapContainer = ref(null)
    const selectedType = ref(null)
    const selectedBusiness = ref(null)
    const favoritesCount = ref(0)

    const selectType = (type) => {
      if (selectedType.value === type) {
        selectedType.value = null
      } else {
        selectedType.value = type
      }
      // TODO: Фильтровать маркеры на карте
      console.log('Selected type:', selectedType.value)
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
      $q.notify({
        type: 'info',
        message: 'Форма записи будет реализована на следующем этапе'
      })
      console.log('Book service at:', business.name)
    }

    onMounted(() => {
      // TODO: Инициализация 2GIS карты
      console.log('MapPage mounted, map container:', mapContainer.value)

      // Временная заглушка с тестовым бизнесом
      setTimeout(() => {
        selectedBusiness.value = {
          name: 'Тестовая автомойка',
          type: 'car_wash',
          address: 'ул. Ленина, 10, Тюмень',
          phone: '+79001234567',
          status: 'available'
        }
      }, 1000)
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
      bookService
    }
  }
})
</script>
