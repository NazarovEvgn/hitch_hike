<template>
  <q-dialog v-model="isOpen" persistent>
    <q-card style="width: 100%; max-width: 600px">
      <!-- Header -->
      <q-card-section class="row items-center q-pb-none bg-primary text-white">
        <div class="text-h6">Онлайн-запись</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <!-- Business Info -->
      <q-card-section v-if="business" class="q-pt-sm bg-grey-2">
        <div class="text-subtitle2">{{ business.name }}</div>
        <div class="text-caption text-grey-7">{{ business.address }}</div>
      </q-card-section>

      <!-- Stepper -->
      <q-stepper
        v-model="step"
        ref="stepper"
        color="primary"
        animated
        flat
      >
        <!-- Step 1: Select Service -->
        <q-step
          :name="1"
          title="Выберите услугу"
          icon="car_wash"
          :done="step > 1"
        >
          <div v-if="loadingServices" class="text-center q-pa-md">
            <q-spinner color="primary" size="3em" />
            <div class="q-mt-md text-grey-7">Загрузка услуг...</div>
          </div>

          <div v-else-if="services.length === 0" class="text-center q-pa-md text-grey-7">
            <q-icon name="warning" size="3em" color="orange" />
            <div class="q-mt-md">Услуги не найдены</div>
          </div>

          <div v-else class="q-gutter-sm">
            <q-card
              v-for="service in services"
              :key="service.id"
              flat
              bordered
              clickable
              :class="{'bg-primary-1 border-primary': selectedService?.id === service.id}"
              @click="selectService(service)"
            >
              <q-card-section class="row items-center">
                <div class="col">
                  <div class="text-subtitle1">{{ service.name }}</div>
                  <div class="text-caption text-grey-7">{{ service.description }}</div>
                  <div class="text-caption q-mt-xs">
                    <q-chip dense size="sm" color="primary" text-color="white">
                      {{ service.price }} ₽
                    </q-chip>
                    <q-chip dense size="sm" color="grey-5" text-color="white">
                      {{ service.duration_minutes }} мин
                    </q-chip>
                  </div>
                </div>
                <div v-if="selectedService?.id === service.id">
                  <q-icon name="check_circle" color="primary" size="md" />
                </div>
              </q-card-section>
            </q-card>
          </div>

          <q-stepper-navigation class="q-mt-md">
            <q-btn
              color="primary"
              label="Далее"
              :disable="!selectedService"
              @click="nextStep"
              unelevated
            />
          </q-stepper-navigation>
        </q-step>

        <!-- Step 2: Select Date & Time -->
        <q-step
          :name="2"
          title="Выберите дату и время"
          icon="event"
          :done="step > 2"
        >
          <div class="row q-col-gutter-md">
            <!-- Calendar -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">Дата</div>
              <q-date
                v-model="selectedDate"
                :options="dateOptions"
                minimal
                flat
                bordered
                mask="YYYY-MM-DD"
                today-btn
              />
            </div>

            <!-- Time Slots -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">Время</div>

              <div v-if="!selectedDate" class="text-center q-pa-md text-grey-7">
                Выберите дату
              </div>

              <div v-else class="q-gutter-xs">
                <q-btn
                  v-for="slot in timeSlots"
                  :key="slot"
                  :label="slot"
                  :color="selectedTime === slot ? 'primary' : 'grey-3'"
                  :text-color="selectedTime === slot ? 'white' : 'dark'"
                  unelevated
                  no-caps
                  size="md"
                  style="width: 80px"
                  @click="selectedTime = slot"
                />
              </div>
            </div>
          </div>

          <q-stepper-navigation class="q-mt-md">
            <q-btn flat color="grey-7" label="Назад" @click="prevStep" />
            <q-btn
              color="primary"
              label="Далее"
              :disable="!selectedDate || !selectedTime"
              @click="nextStep"
              unelevated
            />
          </q-stepper-navigation>
        </q-step>

        <!-- Step 3: Contact Info -->
        <q-step
          :name="3"
          title="Контактные данные"
          icon="person"
          :done="step > 3"
        >
          <q-form @submit.prevent="nextStep" class="q-gutter-md">
            <q-input
              v-model="clientName"
              label="Ваше имя *"
              outlined
              :rules="[val => !!val || 'Введите ваше имя']"
            />

            <q-input
              v-model="clientPhone"
              label="Телефон *"
              outlined
              mask="+7 (###) ###-##-##"
              fill-mask
              unmasked-value
              placeholder="+7 (912) 991-27-81"
              hint="Введите 10 цифр номера после +7"
              :rules="[
                val => !!val || 'Введите номер телефона',
                val => val.length === 10 || 'Введите корректный номер (10 цифр)'
              ]"
            />

            <q-input
              v-model="notes"
              label="Комментарий (необязательно)"
              outlined
              type="textarea"
              rows="2"
              hint="Например: номер автомобиля, особые пожелания"
            />

            <q-stepper-navigation>
              <q-btn flat color="grey-7" label="Назад" @click="prevStep" />
              <q-btn
                type="submit"
                color="primary"
                label="Далее"
                :disable="!clientName || !clientPhone || clientPhone.length !== 10"
                unelevated
              />
            </q-stepper-navigation>
          </q-form>
        </q-step>

        <!-- Step 4: Confirmation -->
        <q-step
          :name="4"
          title="Подтверждение"
          icon="done"
        >
          <div class="q-pa-md">
            <div class="text-h6 q-mb-md">Проверьте данные записи</div>

            <q-list bordered separator>
              <q-item>
                <q-item-section avatar>
                  <q-icon name="car_wash" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Услуга</q-item-label>
                  <q-item-label caption>{{ selectedService?.name }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>{{ selectedService?.price }} ₽</q-item-label>
                  <q-item-label caption>{{ selectedService?.duration_minutes }} мин</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="event" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Дата и время</q-item-label>
                  <q-item-label caption>{{ formatDate(selectedDate) }} в {{ selectedTime }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item>
                <q-item-section avatar>
                  <q-icon name="person" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Контакты</q-item-label>
                  <q-item-label caption>{{ clientName }}</q-item-label>
                  <q-item-label caption>+7{{ clientPhone }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="notes">
                <q-item-section avatar>
                  <q-icon name="comment" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>Комментарий</q-item-label>
                  <q-item-label caption>{{ notes }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <div class="q-mt-md text-caption text-grey-7">
              После записи вам придёт SMS с подтверждением
            </div>
          </div>

          <q-stepper-navigation>
            <q-btn flat color="grey-7" label="Назад" @click="prevStep" />
            <q-btn
              color="primary"
              label="Записаться"
              :loading="submitting"
              @click="submitBooking"
              unelevated
            />
          </q-stepper-navigation>
        </q-step>
      </q-stepper>
    </q-card>
  </q-dialog>
</template>

<script>
import { defineComponent, ref, computed, watch } from 'vue'
import { useQuasar, date } from 'quasar'
import { api } from 'boot/axios'

export default defineComponent({
  name: 'BookingDialog',

  props: {
    modelValue: Boolean,
    business: Object
  },

  emits: ['update:modelValue', 'booking-created'],

  setup(props, { emit }) {
    const $q = useQuasar()
    const stepper = ref(null)
    const step = ref(1)

    // Dialog state
    const isOpen = computed({
      get: () => props.modelValue,
      set: (val) => emit('update:modelValue', val)
    })

    // Step 1: Service selection
    const services = ref([])
    const loadingServices = ref(false)
    const selectedService = ref(null)

    // Step 2: Date & Time selection
    const selectedDate = ref(null)
    const selectedTime = ref(null)

    // Step 3: Contact info
    const clientName = ref('')
    const clientPhone = ref('')
    const notes = ref('')

    // Step 4: Submission
    const submitting = ref(false)

    // Time slots (9:00 - 20:00, every 30 minutes)
    const timeSlots = computed(() => {
      const slots = []
      for (let hour = 9; hour <= 20; hour++) {
        slots.push(`${hour.toString().padStart(2, '0')}:00`)
        if (hour < 20) {
          slots.push(`${hour.toString().padStart(2, '0')}:30`)
        }
      }
      return slots
    })

    // Date validation (only future dates)
    const dateOptions = (dateStr) => {
      const today = date.formatDate(new Date(), 'YYYY/MM/DD')
      return dateStr >= today
    }

    // Format date for display
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return date.formatDate(dateStr, 'DD MMMM YYYY', {
        months: ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
      })
    }

    // Load services when business changes
    watch(() => props.business, async (newBusiness) => {
      if (newBusiness && isOpen.value) {
        await loadServices(newBusiness.id)
      }
    }, { immediate: true })

    // Load services
    const loadServices = async (businessId) => {
      try {
        loadingServices.value = true
        const response = await api.get(`/businesses/${businessId}/services`)
        services.value = response.data.filter(s => s.is_active)
      } catch (error) {
        console.error('Failed to load services:', error)
        $q.notify({
          type: 'negative',
          message: 'Не удалось загрузить услуги'
        })
      } finally {
        loadingServices.value = false
      }
    }

    // Select service
    const selectService = (service) => {
      selectedService.value = service
    }

    // Navigation
    const nextStep = () => {
      step.value++
    }

    const prevStep = () => {
      step.value--
    }

    // Submit booking
    const submitBooking = async () => {
      try {
        submitting.value = true

        const bookingData = {
          business_id: props.business.id,
          service_id: selectedService.value.id,
          booking_date: selectedDate.value,
          booking_time: selectedTime.value,
          client_name: clientName.value,
          client_phone: `+7${clientPhone.value}`,
          notes: notes.value || null
        }

        const response = await api.post('/bookings', bookingData)

        $q.notify({
          type: 'positive',
          message: '✅ Вы успешно записались!',
          caption: `${props.business.name} • ${formatDate(selectedDate.value)} в ${selectedTime.value}`,
          timeout: 3000
        })

        emit('booking-created', response.data)
        closeDialog()
      } catch (error) {
        console.error('Booking failed:', error)
        $q.notify({
          type: 'negative',
          message: error.response?.data?.detail || 'Не удалось создать запись'
        })
      } finally {
        submitting.value = false
      }
    }

    // Close and reset
    const closeDialog = () => {
      isOpen.value = false
      setTimeout(resetForm, 300)
    }

    const resetForm = () => {
      step.value = 1
      selectedService.value = null
      selectedDate.value = null
      selectedTime.value = null
      clientName.value = ''
      clientPhone.value = ''
      notes.value = ''
    }

    return {
      isOpen,
      stepper,
      step,
      services,
      loadingServices,
      selectedService,
      selectedDate,
      selectedTime,
      clientName,
      clientPhone,
      notes,
      submitting,
      timeSlots,
      dateOptions,
      formatDate,
      selectService,
      nextStep,
      prevStep,
      submitBooking,
      closeDialog
    }
  }
})
</script>

<style scoped>
.border-primary {
  border: 2px solid var(--q-primary) !important;
}
</style>
