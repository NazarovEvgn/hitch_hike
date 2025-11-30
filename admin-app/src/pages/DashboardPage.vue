<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">Главная панель</div>

    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-8">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">Текущий статус</div>

            <div class="row q-col-gutter-md">
              <!-- Свободны -->
              <div class="col-12 col-sm-6">
                <q-btn
                  size="lg"
                  class="full-width"
                  :color="currentStatus === 'available' ? 'positive' : 'grey-3'"
                  :text-color="currentStatus === 'available' ? 'white' : 'black'"
                  @click="selectStatus('available')"
                >
                  <div class="column items-center q-pa-sm">
                    <div class="text-h4">🟢</div>
                    <div class="text-subtitle1 q-mt-sm">Свободны</div>
                  </div>
                </q-btn>
              </div>

              <!-- Работаем -->
              <div class="col-12 col-sm-6">
                <q-btn
                  size="lg"
                  class="full-width"
                  :color="currentStatus === 'busy' ? 'warning' : 'grey-3'"
                  :text-color="currentStatus === 'busy' ? 'white' : 'black'"
                  @click="selectStatus('busy')"
                >
                  <div class="column items-center q-pa-sm">
                    <div class="text-h4">🟡</div>
                    <div class="text-subtitle1 q-mt-sm">Работаем</div>
                  </div>
                </q-btn>
              </div>
            </div>

            <!-- Поле времени ожидания (показывается только для статуса "busy") -->
            <div v-if="currentStatus === 'busy'" class="q-mt-md">
              <q-input
                v-model.number="waitMinutes"
                type="number"
                label="Примерное время ожидания (минуты)"
                outlined
                dense
                min="1"
                hint="Укажите примерное время ожидания"
              />
            </div>

            <!-- Кнопка сохранения -->
            <q-btn
              color="primary"
              label="Сохранить статус"
              icon="save"
              class="q-mt-md full-width"
              @click="updateStatus"
              :loading="statusLoading"
            />

            <!-- Текущий отображаемый статус -->
            <div class="q-mt-md q-pa-md bg-grey-2 rounded-borders">
              <div class="text-caption text-grey-7">Отображается клиентам:</div>
              <div class="text-body1 text-weight-medium" :class="`text-${statusColor}`">
                {{ displayStatusText }}
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card clickable @click="$router.push({ name: 'bookings' })" class="cursor-pointer">
          <q-card-section>
            <div class="text-h6">Онлайн-запись сегодня</div>
            <div class="text-h3 text-primary">{{ stats.todayBookings }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Быстрые действия</div>
        <div class="row q-col-gutter-sm">
          <div class="col-12 col-sm-6 col-md-4">
            <q-btn
              color="secondary"
              icon="event"
              label="Онлайн-записи"
              class="full-width"
              :to="{ name: 'bookings' }"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-4">
            <q-btn
              color="accent"
              icon="build"
              label="Услуги"
              class="full-width"
              :to="{ name: 'services' }"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-4">
            <q-btn
              color="orange"
              icon="local_offer"
              label="Акции"
              class="full-width"
              :to="{ name: 'promotions' }"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'DashboardPage',

  setup() {
    const $q = useQuasar()

    // Статистика
    const stats = ref({
      todayBookings: 0
    })

    // Статус
    const currentStatus = ref('available')
    const waitMinutes = ref(15)
    const statusLoading = ref(false)
    const dataLoading = ref(false)

    // Выбор статуса
    const selectStatus = (status) => {
      currentStatus.value = status
      if (status === 'available') {
        waitMinutes.value = 0
      } else if (waitMinutes.value === 0) {
        waitMinutes.value = 15
      }
    }

    // Цвет статуса
    const statusColor = computed(() => {
      return currentStatus.value === 'available' ? 'positive' : 'warning'
    })

    // Текст для отображения клиентам
    const displayStatusText = computed(() => {
      if (currentStatus.value === 'available') {
        return 'Свободны. Готовы принять сразу'
      } else {
        return `Работаем. Примерное время ожидания ${waitMinutes.value} мин`
      }
    })

    // Загрузка текущего статуса
    const loadStatus = async () => {
      try {
        dataLoading.value = true
        const response = await api.get('/admin/status')

        currentStatus.value = response.data.status
        waitMinutes.value = response.data.estimated_wait_minutes || 0
      } catch (error) {
        console.error('Failed to load status:', error)
      } finally {
        dataLoading.value = false
      }
    }

    // Обновление статуса
    const updateStatus = async () => {
      try {
        statusLoading.value = true

        await api.patch('/admin/status', {
          status: currentStatus.value,
          estimated_wait_minutes: currentStatus.value === 'busy' ? waitMinutes.value : 0,
          current_queue_count: 0
        })

        $q.notify({
          type: 'positive',
          message: 'Статус успешно обновлен!',
          icon: 'check_circle'
        })
      } catch (error) {
        console.error('Failed to update status:', error)
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
    })

    return {
      stats,
      currentStatus,
      waitMinutes,
      statusLoading,
      selectStatus,
      statusColor,
      displayStatusText,
      updateStatus
    }
  }
})
</script>
