<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">Онлайн-записи</div>

    <!-- Фильтры -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <q-select
              v-model="filters.status"
              :options="statusOptions"
              label="Статус"
              outlined
              clearable
              @update:model-value="fetchBookings"
            />
          </div>
          <div class="col-12 col-md-6 flex items-center">
            <q-btn
              color="primary"
              icon="refresh"
              label="Обновить"
              @click="fetchBookings"
              :loading="loading"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Таблица бронирований -->
    <q-card>
      <q-card-section>
        <q-table
          :rows="bookings"
          :columns="columns"
          row-key="id"
          :loading="loading"
          flat
          bordered
          :rows-per-page-options="[10, 25, 50]"
          :grid="$q.screen.lt.md"
        >
          <template v-slot:body-cell-booking_datetime="props">
            <q-td :props="props">
              <div>{{ formatDate(props.row.booking_date) }}</div>
              <div class="text-caption text-grey">{{ props.row.booking_time }}</div>
            </q-td>
          </template>

          <template v-slot:body-cell-client="props">
            <q-td :props="props">
              <div>{{ props.row.client_name }}</div>
              <div class="text-caption">{{ props.row.client_phone }}</div>
            </q-td>
          </template>

          <template v-slot:body-cell-service="props">
            <q-td :props="props">
              {{ props.row.service?.name || '-' }}
            </q-td>
          </template>

          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <q-badge :color="getStatusColor(props.row.status)">
                {{ getStatusLabel(props.row.status) }}
              </q-badge>
            </q-td>
          </template>

          <template v-slot:body-cell-came_through_app="props">
            <q-td :props="props">
              <q-icon
                :name="props.row.came_through_app ? 'check_circle' : 'cancel'"
                :color="props.row.came_through_app ? 'positive' : 'grey'"
                size="sm"
              >
                <q-tooltip>
                  {{ props.row.came_through_app ? 'Пришел через приложение' : 'Не через приложение' }}
                </q-tooltip>
              </q-icon>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn
                flat
                dense
                round
                icon="visibility"
                color="primary"
                @click="viewBookingDetails(props.row)"
              >
                <q-tooltip>Подробности</q-tooltip>
              </q-btn>
              <q-btn
                v-if="props.row.status === 'pending'"
                flat
                dense
                round
                icon="check"
                color="positive"
                @click="updateBookingStatus(props.row, 'confirmed')"
              >
                <q-tooltip>Подтвердить</q-tooltip>
              </q-btn>
              <q-btn
                v-if="props.row.status === 'confirmed'"
                flat
                dense
                round
                icon="done_all"
                color="primary"
                @click="updateBookingStatus(props.row, 'completed')"
              >
                <q-tooltip>Завершить</q-tooltip>
              </q-btn>
              <q-btn
                v-if="['pending', 'confirmed'].includes(props.row.status)"
                flat
                dense
                round
                icon="close"
                color="negative"
                @click="updateBookingStatus(props.row, 'cancelled')"
              >
                <q-tooltip>Отменить</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <!-- Grid mode для мобильных устройств -->
          <template v-slot:item="props">
            <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4">
              <q-card>
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <div class="col">
                      <div class="text-subtitle1 text-weight-medium">
                        {{ props.row.client_name }}
                      </div>
                      <div class="text-caption text-grey">
                        {{ props.row.client_phone }}
                      </div>
                    </div>
                    <div class="col-auto">
                      <q-badge :color="getStatusColor(props.row.status)">
                        {{ getStatusLabel(props.row.status) }}
                      </q-badge>
                    </div>
                  </div>

                  <q-separator class="q-my-sm" />

                  <div class="text-body2">
                    <div class="row q-mb-xs">
                      <div class="col-5 text-grey-7">Дата и время:</div>
                      <div class="col-7">
                        {{ formatDate(props.row.booking_date) }}
                        <div class="text-caption">{{ props.row.booking_time }}</div>
                      </div>
                    </div>
                    <div class="row q-mb-xs">
                      <div class="col-5 text-grey-7">Услуга:</div>
                      <div class="col-7">{{ props.row.service?.name || '-' }}</div>
                    </div>
                    <div v-if="props.row.notes" class="row q-mb-xs">
                      <div class="col-5 text-grey-7">Примечания:</div>
                      <div class="col-7 text-caption">{{ props.row.notes }}</div>
                    </div>
                  </div>
                </q-card-section>

                <q-separator />

                <q-card-actions align="right">
                  <q-btn
                    flat
                    dense
                    icon="visibility"
                    color="primary"
                    label="Детали"
                    @click="viewBookingDetails(props.row)"
                  />
                  <q-btn
                    v-if="props.row.status === 'pending'"
                    flat
                    dense
                    icon="check"
                    color="positive"
                    label="Подтвердить"
                    @click="updateBookingStatus(props.row, 'confirmed')"
                  />
                  <q-btn
                    v-if="props.row.status === 'confirmed'"
                    flat
                    dense
                    icon="done_all"
                    color="primary"
                    label="Завершить"
                    @click="updateBookingStatus(props.row, 'completed')"
                  />
                  <q-btn
                    v-if="['pending', 'confirmed'].includes(props.row.status)"
                    flat
                    dense
                    icon="close"
                    color="negative"
                    @click="updateBookingStatus(props.row, 'cancelled')"
                  />
                </q-card-actions>
              </q-card>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Диалог подробностей бронирования -->
    <q-dialog v-model="detailsDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Детали бронирования</div>
        </q-card-section>

        <q-card-section v-if="selectedBooking" class="q-pt-none">
          <q-list bordered separator>
            <q-item>
              <q-item-section>
                <q-item-label caption>Дата и время</q-item-label>
                <q-item-label>
                  {{ formatDate(selectedBooking.booking_date) }}, {{ selectedBooking.booking_time }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Клиент</q-item-label>
                <q-item-label>{{ selectedBooking.client_name }}</q-item-label>
                <q-item-label caption>{{ selectedBooking.client_phone }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Услуга</q-item-label>
                <q-item-label>{{ selectedBooking.service?.name || '-' }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Статус</q-item-label>
                <q-item-label>
                  <q-badge :color="getStatusColor(selectedBooking.status)">
                    {{ getStatusLabel(selectedBooking.status) }}
                  </q-badge>
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item v-if="selectedBooking.notes">
              <q-item-section>
                <q-item-label caption>Примечания</q-item-label>
                <q-item-label>{{ selectedBooking.notes }}</q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Источник</q-item-label>
                <q-item-label>
                  <q-icon
                    :name="selectedBooking.came_through_app ? 'smartphone' : 'phone'"
                    :color="selectedBooking.came_through_app ? 'positive' : 'grey'"
                  />
                  {{ selectedBooking.came_through_app ? 'Через приложение' : 'Телефон/другое' }}
                </q-item-label>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label caption>Создано</q-item-label>
                <q-item-label>{{ formatDateTime(selectedBooking.created_at) }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">Изменить статус:</div>
            <div class="row q-col-gutter-sm">
              <div class="col-6" v-if="selectedBooking.status === 'pending'">
                <q-btn
                  color="positive"
                  label="Подтвердить"
                  icon="check"
                  class="full-width"
                  @click="updateBookingStatus(selectedBooking, 'confirmed')"
                />
              </div>
              <div class="col-6" v-if="selectedBooking.status === 'confirmed'">
                <q-btn
                  color="primary"
                  label="Завершить"
                  icon="done_all"
                  class="full-width"
                  @click="updateBookingStatus(selectedBooking, 'completed')"
                />
              </div>
              <div class="col-6" v-if="['pending', 'confirmed'].includes(selectedBooking.status)">
                <q-btn
                  color="negative"
                  label="Отменить"
                  icon="close"
                  class="full-width"
                  @click="updateBookingStatus(selectedBooking, 'cancelled')"
                />
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Закрыть" color="grey" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'BookingsPage',

  setup() {
    const $q = useQuasar()
    const bookings = ref([])
    const loading = ref(false)
    const detailsDialog = ref(false)
    const selectedBooking = ref(null)

    const filters = ref({
      status: null
    })

    const statusOptions = [
      { label: 'Все', value: null },
      { label: 'Ожидает', value: 'pending' },
      { label: 'Подтверждено', value: 'confirmed' },
      { label: 'Завершено', value: 'completed' },
      { label: 'Отменено', value: 'cancelled' }
    ]

    const columns = [
      {
        name: 'booking_datetime',
        label: 'Дата и время',
        align: 'left',
        field: 'booking_date',
        sortable: true
      },
      {
        name: 'client',
        label: 'Клиент',
        align: 'left',
        field: 'client_name',
        sortable: true
      },
      {
        name: 'service',
        label: 'Услуга',
        align: 'left',
        sortable: false
      },
      {
        name: 'status',
        label: 'Статус',
        align: 'center',
        field: 'status',
        sortable: true
      },
      {
        name: 'came_through_app',
        label: 'Через приложение',
        align: 'center',
        field: 'came_through_app',
        sortable: true
      },
      {
        name: 'actions',
        label: 'Действия',
        align: 'center'
      }
    ]

    const getStatusColor = (status) => {
      const colors = {
        pending: 'orange',
        confirmed: 'blue',
        completed: 'positive',
        cancelled: 'negative'
      }
      return colors[status] || 'grey'
    }

    const getStatusLabel = (status) => {
      const labels = {
        pending: 'Ожидает',
        confirmed: 'Подтверждено',
        completed: 'Завершено',
        cancelled: 'Отменено'
      }
      return labels[status] || status
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const fetchBookings = async () => {
      loading.value = true
      try {
        const params = {}
        if (filters.value.status) params.status = filters.value.status.value || filters.value.status

        const response = await api.get('/admin/bookings', { params })
        bookings.value = response.data
      } catch (error) {
        $q.notify({
          type: 'negative',
          message: 'Ошибка загрузки бронирований',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loading.value = false
      }
    }

    const viewBookingDetails = (booking) => {
      selectedBooking.value = booking
      detailsDialog.value = true
    }

    const updateBookingStatus = async (booking, newStatus) => {
      try {
        await api.patch(`/admin/bookings/${booking.id}`, {
          status: newStatus
        })
        booking.status = newStatus
        if (selectedBooking.value && selectedBooking.value.id === booking.id) {
          selectedBooking.value.status = newStatus
        }
        $q.notify({
          type: 'positive',
          message: `Статус изменен на "${getStatusLabel(newStatus)}"`
        })
        await fetchBookings()
      } catch (error) {
        $q.notify({
          type: 'negative',
          message: 'Ошибка изменения статуса',
          caption: error.response?.data?.detail || error.message
        })
      }
    }

    onMounted(() => {
      fetchBookings()
    })

    return {
      bookings,
      loading,
      columns,
      filters,
      statusOptions,
      detailsDialog,
      selectedBooking,
      getStatusColor,
      getStatusLabel,
      formatDate,
      formatDateTime,
      fetchBookings,
      viewBookingDetails,
      updateBookingStatus
    }
  }
})
</script>
