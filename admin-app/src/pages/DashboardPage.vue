<template>
  <q-page padding class="column" style="min-height: calc(100vh - 50px)">
    <!-- Раздел статуса (компактный) -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-sm">Статус</div>

        <div class="row items-center justify-between">
          <div class="text-body1">Свободны. Можем принять в ближайшее время</div>
          <q-toggle
            v-model="isAvailable"
            color="positive"
            size="lg"
            @update:model-value="updateStatus"
            :loading="statusLoading"
          />
        </div>

        <div v-if="isAvailable" class="q-mt-sm text-caption text-dark">
          ✓ Статус "Свободен" отображается клиентам
        </div>
        <div v-else class="q-mt-sm text-caption text-grey">
          Статус не отображается клиентам
        </div>
      </q-card-section>
    </q-card>

    <!-- Раздел онлайн-записей -->
    <q-card class="q-mb-md" clickable @click="$router.push({ name: 'bookings' })">
      <q-card-section class="row items-center justify-between">
        <div>
          <div class="text-h6">Онлайн-записи</div>
          <div class="text-caption text-grey-7">Записей сегодня</div>
        </div>
        <div class="text-h3 text-primary">{{ todayBookingsCount }}</div>
      </q-card-section>
    </q-card>

    <q-space />

    <!-- Footer с быстрой навигацией -->
    <div class="row q-col-gutter-sm q-mt-md">
      <div class="col-6">
        <q-btn
          color="primary"
          label="Услуги и цены"
          class="full-width"
          :to="{ name: 'services' }"
        />
      </div>
      <div class="col-6">
        <q-btn
          color="primary"
          label="Личный кабинет"
          class="full-width"
          :to="{ name: 'profile' }"
        />
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'DashboardPage',

  setup() {
    const $q = useQuasar()

    const isAvailable = ref(true)
    const statusLoading = ref(false)
    const todayBookingsCount = ref(0)

    // Загрузка текущего статуса
    const loadStatus = async () => {
      try {
        const response = await api.get('/admin/status/current')
        isAvailable.value = response.data.status === 'available'
      } catch (error) {
        console.error('Failed to load status:', error)
      }
    }

    // Загрузка статистики записей
    const loadBookingsStats = async () => {
      try {
        const response = await api.get('/admin/bookings')
        // Подсчет записей на сегодня
        const today = new Date().toISOString().split('T')[0]
        todayBookingsCount.value = response.data.filter(booking =>
          booking.booking_date === today
        ).length
      } catch (error) {
        console.error('Failed to load bookings stats:', error)
      }
    }

    // Обновление статуса
    const updateStatus = async (value) => {
      try {
        statusLoading.value = true

        await api.patch('/admin/status', {
          status: value ? 'available' : 'busy',
          estimated_wait_minutes: 0,
          current_queue_count: 0
        })

        $q.notify({
          type: 'positive',
          message: value ? 'Статус "Свободен" установлен' : 'Статус снят',
          icon: 'check_circle'
        })
      } catch (error) {
        console.error('Failed to update status:', error)
        isAvailable.value = !value // Откатываем изменение
        $q.notify({
          type: 'negative',
          message: error.response?.data?.detail || 'Ошибка при обновлении статуса'
        })
      } finally {
        statusLoading.value = false
      }
    }

    // Загрузка данных при монтировании
    onMounted(() => {
      loadStatus()
      loadBookingsStats()
    })

    return {
      isAvailable,
      statusLoading,
      todayBookingsCount,
      updateStatus
    }
  }
})
</script>
