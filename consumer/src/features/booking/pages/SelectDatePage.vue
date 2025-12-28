<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-button @click="router.back()" class="back-button">
            <ion-icon slot="icon-only" :icon="arrowBackOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
        <ion-title slot="end" class="header-title">Выберите дату и время</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="page-content">
        <!-- Calendar Section -->
        <div class="calendar-section">
          <div class="calendar-container">
            <ion-datetime
              v-model="selectedDate"
              presentation="date"
              :min="minDate"
              :max="maxDate"
              locale="ru-RU"
              :first-day-of-week="1"
              :show-default-title="false"
              :show-default-buttons="false"
              @ionChange="handleDateChange"
              class="custom-calendar"
            >
            </ion-datetime>
          </div>
        </div>

        <!-- Time Slots Section -->
        <div class="time-slots-section">
          <!-- Loading -->
          <div v-if="loadingSlots" class="loading-container">
            <ion-spinner name="crescent"></ion-spinner>
          </div>

          <!-- Time Slots Grid -->
          <div v-else-if="!loadingSlots && timeSlots.length > 0" class="time-slots-grid">
            <div
              v-for="slot in timeSlots"
              :key="slot.time"
              class="time-slot"
              :class="{ 'time-slot-selected': slot.time === selectedTime }"
              @click="selectTime(slot.time)"
            >
              {{ slot.time }}
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="empty-state">
            <p>Нет доступных слотов на выбранную дату</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <ion-button
            expand="block"
            :disabled="!selectedTime"
            @click="confirmBooking"
            class="confirm-button"
          >
            Подтвердить запись
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonButton,
  IonIcon,
  IonTitle,
  IonContent,
  IonDatetime,
  IonSpinner,
  alertController,
} from '@ionic/vue'
import { arrowBackOutline } from 'ionicons/icons'
import { useBookingStore } from '../stores/bookingStore'
import type { TimeSlot } from '../types'

const router = useRouter()
const route = useRoute()
const bookingStore = useBookingStore()

const businessId = ref<number>(parseInt(route.params.businessId as string))
const serviceId = ref<number>(parseInt(route.params.serviceId as string))
const employeeId = ref<number>(parseInt(route.params.employeeId as string))

const selectedDate = ref<string | null>(null)
const selectedTime = ref<string | null>(null)
const timeSlots = ref<TimeSlot[]>([])
const loadingSlots = ref(false)
const minDate = ref<string>('')
const maxDate = ref<string>('')

async function handleDateChange(event: CustomEvent) {
  const value = event.detail.value
  console.log('[SelectDatePage] Date changed:', value)
  if (value) {
    // Extract just the date part (YYYY-MM-DD)
    const dateStr = value.split('T')[0]
    selectedDate.value = dateStr
    selectedTime.value = null
    bookingStore.selectDate(dateStr)

    console.log('[SelectDatePage] Loading slots for date:', dateStr)
    await loadTimeSlots()
  }
}

// Load time slots for selected date
async function loadTimeSlots() {
  if (!selectedDate.value) {
    console.log('[SelectDatePage] No date selected, skipping slot load')
    return
  }

  loadingSlots.value = true
  console.log('[SelectDatePage] Loading slots for:', selectedDate.value, 'employee:', employeeId.value)

  try {
    await bookingStore.fetchAvailableSlots(employeeId.value, selectedDate.value)

    console.log('[SelectDatePage] Available slots from store:', bookingStore.availableSlots)

    // Convert available slots to time slots
    const slots = bookingStore.availableSlots.filter(s => s.date === selectedDate.value)
    console.log('[SelectDatePage] Filtered slots for date:', slots)

    timeSlots.value = slots.map(s => ({
      time: s.time,
      available: true,
      employee_id: s.employee_id,
    }))

    console.log('[SelectDatePage] Time slots set:', timeSlots.value)
    console.log('[SelectDatePage] Time slots length:', timeSlots.value.length)
  } catch (err) {
    console.error('[SelectDatePage] Error loading time slots:', err)
  } finally {
    loadingSlots.value = false
    console.log('[SelectDatePage] Loading finished. loadingSlots:', loadingSlots.value, 'timeSlots.length:', timeSlots.value.length)
  }
}

// Select time
function selectTime(time: string) {
  selectedTime.value = time
  bookingStore.selectTime(time)
}

// Confirm booking
async function confirmBooking() {
  if (!selectedTime.value) return

  const success = await bookingStore.submitBooking()

  if (success) {
    const alert = await alertController.create({
      header: 'Запись подтверждена',
      message: `Вы записаны на ${selectedDate.value} в ${selectedTime.value}`,
      buttons: [
        {
          text: 'OK',
          handler: () => {
            router.push('/home')
          },
        },
      ],
    })

    await alert.present()
  } else {
    const alert = await alertController.create({
      header: 'Ошибка',
      message: bookingStore.error || 'Не удалось создать запись',
      buttons: ['OK'],
    })

    await alert.present()
  }
}

onMounted(async () => {
  // Set min date to today
  const today = new Date()
  minDate.value = today.toISOString()

  // Set max date to 60 days from now
  const maxDateObj = new Date()
  maxDateObj.setDate(maxDateObj.getDate() + 60)
  maxDate.value = maxDateObj.toISOString()

  // Set default selected date to today
  selectedDate.value = today.toISOString().split('T')[0]
  bookingStore.selectDate(selectedDate.value)

  // Load time slots for today
  await loadTimeSlots()
})
</script>

<style scoped>
ion-header {
  box-shadow: none;
}

ion-header ion-toolbar {
  --background: transparent;
  --border-width: 0;
  --box-shadow: none;
}

.back-button {
  --color: var(--ion-color-primary);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  padding-right: 24px;
  text-align: right;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

ion-content {
  --background: #f5f5f5;
}

.page-content {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding-bottom: 80px;
  overflow-y: auto;
}

/* Calendar Section */
.calendar-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.calendar-container {
  background: rgba(138, 43, 226, 0.08);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(138, 43, 226, 0.15);
  overflow: hidden;
  max-height: 400px;
  max-width: 360px;
  width: 100%;
}

.custom-calendar {
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
  border-radius: 16px;
  max-height: 380px;
  --padding-start: 0;
  --padding-end: 0;
  --background: transparent;
  --background-rgb: 0, 0, 0;
  color: #000000;
}

/* Черный шрифт для календаря */
.custom-calendar::part(calendar-day) {
  color: #000000;
}

/* Белый шрифт для выбранной даты */
.custom-calendar::part(calendar-day-active),
.custom-calendar::part(calendar-day active) {
  color: #ffffff !important;
}

.custom-calendar::part(month-year-button) {
  color: #000000;
}

/* Убрать внутренние отступы календаря */
.custom-calendar::part(calendar) {
  padding: 0;
  background: transparent;
}

.custom-calendar::part(calendar-body) {
  padding: 0;
  background: transparent;
}

/* Скрыть header календаря */
.custom-calendar::part(calendar-header) {
  display: none;
}

.custom-calendar::part(title) {
  display: none;
}

/* Отключить клик на месяц/год - только стрелочки */
.custom-calendar::part(month-year-button) {
  pointer-events: none;
  cursor: default;
}

/* Убрать стрелочку вниз у кнопки месяца/года */
ion-datetime::part(month-year-button)::after,
ion-datetime::part(month-year-button)::before {
  display: none !important;
  content: none !important;
}

/* Скрыть иконку dropdown через content */
.custom-calendar::part(month-year-button) ion-icon {
  display: none !important;
}

/* Time Slots Section */
.time-slots-section {
  flex-shrink: 0;
  padding: 0 16px;
  margin-bottom: 16px;
  min-height: 200px;
}

.time-slots-section .section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.time-slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.time-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  border-radius: 12px;
  background: #ffffff;
  border: 2px solid #e0e0e0;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.time-slot:active {
  transform: scale(0.95);
}

.time-slot-selected {
  background: var(--ion-color-primary);
  border-color: var(--ion-color-primary);
  color: #ffffff;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--ion-color-medium);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

/* Action Buttons */
.action-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: #ffffff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.confirm-button {
  --background: var(--ion-color-primary);
  --border-radius: 12px;
  height: 52px;
  font-weight: 600;
  font-size: 16px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.confirm-button:disabled {
  opacity: 0.5;
}
</style>
