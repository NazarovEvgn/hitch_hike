<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">Главная панель</div>

    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="text-h6">Бронирования сегодня</div>
            <div class="text-h3 text-primary">{{ stats.todayBookings }}</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="text-h6">Просмотры профиля</div>
            <div class="text-h3 text-positive">{{ stats.profileViews }}</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section>
            <div class="text-h6">Текущий статус</div>
            <div class="text-h3" :class="`text-${statusColor}`">
              {{ statusText }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Быстрые действия</div>
        <div class="row q-col-gutter-sm">
          <div class="col-12 col-sm-6 col-md-3">
            <q-btn
              color="primary"
              icon="schedule"
              label="Обновить статус"
              class="full-width"
              :to="{ name: 'status' }"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-btn
              color="secondary"
              icon="event"
              label="Бронирования"
              class="full-width"
              :to="{ name: 'bookings' }"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
            <q-btn
              color="accent"
              icon="build"
              label="Услуги"
              class="full-width"
              :to="{ name: 'services' }"
            />
          </div>
          <div class="col-12 col-sm-6 col-md-3">
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
import { defineComponent, ref, computed } from 'vue'

export default defineComponent({
  name: 'DashboardPage',

  setup() {
    const stats = ref({
      todayBookings: 0,
      profileViews: 0,
      currentStatus: 'available'
    })

    const statusColor = computed(() => {
      const colors = {
        available: 'positive',
        busy: 'warning',
        very_busy: 'negative'
      }
      return colors[stats.value.currentStatus] || 'grey'
    })

    const statusText = computed(() => {
      const texts = {
        available: 'Доступен',
        busy: 'Занят',
        very_busy: 'Очень занят'
      }
      return texts[stats.value.currentStatus] || 'Не установлен'
    })

    return {
      stats,
      statusColor,
      statusText
    }
  }
})
</script>
