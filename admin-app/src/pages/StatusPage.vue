<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">Обновление статуса загруженности</div>

    <q-card>
      <q-card-section>
        <div class="text-h6 q-mb-md">Выберите текущий статус</div>

        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <q-btn
              size="xl"
              class="full-width"
              :color="status === 'available' ? 'positive' : 'grey-3'"
              :text-color="status === 'available' ? 'white' : 'black'"
              @click="status = 'available'"
            >
              <div class="column items-center">
                <div class="text-h4">🟢</div>
                <div class="text-h6 q-mt-sm">Доступен</div>
                <div class="text-caption">0-15 мин</div>
              </div>
            </q-btn>
          </div>

          <div class="col-12 col-md-4">
            <q-btn
              size="xl"
              class="full-width"
              :color="status === 'busy' ? 'warning' : 'grey-3'"
              :text-color="status === 'busy' ? 'white' : 'black'"
              @click="status = 'busy'"
            >
              <div class="column items-center">
                <div class="text-h4">🟡</div>
                <div class="text-h6 q-mt-sm">Занят</div>
                <div class="text-caption">15-30 мин</div>
              </div>
            </q-btn>
          </div>

          <div class="col-12 col-md-4">
            <q-btn
              size="xl"
              class="full-width"
              :color="status === 'very_busy' ? 'negative' : 'grey-3'"
              :text-color="status === 'very_busy' ? 'white' : 'black'"
              @click="status = 'very_busy'"
            >
              <div class="column items-center">
                <div class="text-h4">🟠</div>
                <div class="text-h6 q-mt-sm">Очень занят</div>
                <div class="text-caption">30+ мин</div>
              </div>
            </q-btn>
          </div>
        </div>

        <q-input
          v-model.number="waitMinutes"
          type="number"
          label="Примерное время ожидания (минуты)"
          outlined
          class="q-mt-md"
        />

        <q-input
          v-model.number="queueCount"
          type="number"
          label="Текущая очередь (автомобилей)"
          outlined
          class="q-mt-md"
        />

        <q-btn
          color="primary"
          label="Обновить статус"
          icon="save"
          class="q-mt-md full-width"
          size="lg"
          @click="updateStatus"
          :loading="loading"
        />
      </q-card-section>
    </q-card>

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">История обновлений</div>
        <div class="text-caption text-grey-7">Скоро будет доступна история обновлений статуса</div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'StatusPage',

  setup() {
    const $q = useQuasar()
    const status = ref('available')
    const waitMinutes = ref(0)
    const queueCount = ref(0)
    const loading = ref(false)

    const updateStatus = async () => {
      loading.value = true

      try {
        await api.patch('/admin/status', {
          status: status.value,
          estimated_wait_minutes: waitMinutes.value,
          current_queue_count: queueCount.value
        })

        $q.notify({
          type: 'positive',
          message: 'Статус успешно обновлен!'
        })
      } catch (error) {
        $q.notify({
          type: 'negative',
          message: error.response?.data?.detail || 'Ошибка при обновлении статуса'
        })
      } finally {
        loading.value = false
      }
    }

    return {
      status,
      waitMinutes,
      queueCount,
      loading,
      updateStatus
    }
  }
})
</script>
