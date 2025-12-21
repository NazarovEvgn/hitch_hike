<template>
  <div class="business-hours-form">
    <!-- Loading -->
    <div v-if="businessHoursStore.loading && schedules.length === 0" class="loading-container">
      <ion-spinner name="crescent"></ion-spinner>
    </div>

    <!-- Schedule Form -->
    <div v-else>
      <!-- Days List -->
      <ion-list class="days-list">
        <ion-item
          v-for="(day, index) in schedules"
          :key="index"
          lines="full"
          class="day-item"
        >
          <div class="day-content">
            <!-- Day Name -->
            <div class="day-name">{{ day.name }}</div>

            <!-- Is Open Toggle -->
            <div class="day-toggle">
              <ion-toggle
                v-model="day.isOpen"
                @ionChange="validateDay(index)"
                :enable-on-off-labels="true"
              >
                <span slot="label">{{ day.isOpen ? 'Работает' : 'Закрыто' }}</span>
              </ion-toggle>
            </div>

            <!-- Time Inputs -->
            <div v-if="day.isOpen" class="time-inputs">
              <div class="time-input-group">
                <label>Открытие</label>
                <ion-button
                  expand="block"
                  fill="outline"
                  @click="openTimePicker(index, 'open')"
                  class="time-button"
                >
                  {{ day.openTime || 'Выбрать' }}
                </ion-button>
              </div>

              <div class="time-input-group">
                <label>Закрытие</label>
                <ion-button
                  expand="block"
                  fill="outline"
                  @click="openTimePicker(index, 'close')"
                  class="time-button"
                >
                  {{ day.closeTime || 'Выбрать' }}
                </ion-button>
              </div>

              <!-- Copy to All Button -->
              <ion-button
                fill="clear"
                size="small"
                @click="copyToAll(index)"
                class="copy-button"
              >
                <ion-icon slot="icon-only" :icon="copyOutline"></ion-icon>
              </ion-button>
            </div>

            <!-- Error Message -->
            <div v-if="day.error" class="error-message">
              {{ day.error }}
            </div>
          </div>
        </ion-item>
      </ion-list>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <ion-button
          expand="block"
          fill="outline"
          color="medium"
          @click="resetSchedule"
          :disabled="isSaving"
        >
          Сбросить
        </ion-button>

        <ion-button
          expand="block"
          color="primary"
          @click="saveSchedule"
          :disabled="isSaving || hasErrors"
        >
          <ion-spinner v-if="isSaving" name="crescent"></ion-spinner>
          <span v-else>Сохранить</span>
        </ion-button>
      </div>
    </div>

    <!-- Time Picker Modal -->
    <ion-modal :is-open="isTimePickerOpen" @didDismiss="closeTimePicker">
      <ion-header>
        <ion-toolbar>
          <ion-title>{{ timePickerTitle }}</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="closeTimePicker">Отмена</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content class="ion-padding">
        <ion-datetime
          v-model="selectedTime"
          presentation="time"
          :hour-cycle="'h23'"
          :minute-values="minuteValues"
          locale="ru-RU"
        >
          <ion-buttons slot="buttons">
            <ion-button color="primary" @click="confirmTime">Подтвердить</ion-button>
          </ion-buttons>
        </ion-datetime>
      </ion-content>
    </ion-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  IonList,
  IonItem,
  IonToggle,
  IonButton,
  IonButtons,
  IonIcon,
  IonSpinner,
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonDatetime,
  toastController,
} from '@ionic/vue'
import { copyOutline } from 'ionicons/icons'
import { useBusinessHoursStore } from '../stores/businessHoursStore'
import type { DaySchedule } from '../types'

const businessHoursStore = useBusinessHoursStore()

const schedules = ref<DaySchedule[]>([])
const isSaving = ref(false)

// Time picker state
const isTimePickerOpen = ref(false)
const selectedTime = ref<string>('')
const currentDayIndex = ref<number | null>(null)
const currentTimeType = ref<'open' | 'close' | null>(null)

// Generate minute values (every 15 minutes)
const minuteValues = [0, 15, 30, 45]

const hasErrors = computed(() => {
  return schedules.value.some(day => day.error !== null)
})

const timePickerTitle = computed(() => {
  if (currentDayIndex.value === null) return ''
  const day = schedules.value[currentDayIndex.value]
  const timeType = currentTimeType.value === 'open' ? 'Время открытия' : 'Время закрытия'
  return `${day.name} - ${timeType}`
})

onMounted(async () => {
  schedules.value = await businessHoursStore.fetchBusinessHours()
})

function openTimePicker(dayIndex: number, type: 'open' | 'close') {
  currentDayIndex.value = dayIndex
  currentTimeType.value = type

  const day = schedules.value[dayIndex]
  const currentValue = type === 'open' ? day.openTime : day.closeTime

  // Convert HH:MM to ISO datetime format for ion-datetime
  if (currentValue) {
    const today = new Date().toISOString().split('T')[0]
    selectedTime.value = `${today}T${currentValue}:00`
  } else {
    // Default to 9:00 for opening, 18:00 for closing
    const today = new Date().toISOString().split('T')[0]
    const defaultTime = type === 'open' ? '09:00' : '18:00'
    selectedTime.value = `${today}T${defaultTime}:00`
  }

  isTimePickerOpen.value = true
}

function closeTimePicker() {
  isTimePickerOpen.value = false
  currentDayIndex.value = null
  currentTimeType.value = null
  selectedTime.value = ''
}

function confirmTime() {
  if (currentDayIndex.value === null || currentTimeType.value === null) return

  const day = schedules.value[currentDayIndex.value]

  // Extract HH:MM from ISO datetime
  const timeValue = selectedTime.value.split('T')[1].substring(0, 5)

  if (currentTimeType.value === 'open') {
    day.openTime = timeValue
  } else {
    day.closeTime = timeValue
  }

  validateDay(currentDayIndex.value)
  closeTimePicker()
}

function validateDay(index: number) {
  const day = schedules.value[index]

  if (!day.isOpen) {
    day.error = null
    return
  }

  if (!day.openTime || !day.closeTime) {
    day.error = 'Укажите время открытия и закрытия'
    return
  }

  if (day.openTime >= day.closeTime) {
    day.error = 'Время открытия должно быть раньше времени закрытия'
    return
  }

  day.error = null
}

async function copyToAll(sourceIndex: number) {
  const source = schedules.value[sourceIndex]

  schedules.value.forEach((day, index) => {
    if (index !== sourceIndex) {
      day.isOpen = source.isOpen
      day.openTime = source.openTime
      day.closeTime = source.closeTime
      validateDay(index)
    }
  })

  const toast = await toastController.create({
    message: 'Расписание скопировано на все дни',
    duration: 2000,
    color: 'success',
    position: 'top',
  })
  await toast.present()
}

async function resetSchedule() {
  schedules.value = await businessHoursStore.fetchBusinessHours()

  const toast = await toastController.create({
    message: 'Расписание сброшено',
    duration: 2000,
    color: 'medium',
    position: 'top',
  })
  await toast.present()
}

async function saveSchedule() {
  // Validate all days
  schedules.value.forEach((_, index) => validateDay(index))

  if (hasErrors.value) {
    const toast = await toastController.create({
      message: 'Исправьте ошибки перед сохранением',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
    return
  }

  isSaving.value = true

  const result = await businessHoursStore.updateBusinessHours(schedules.value)

  isSaving.value = false

  if (result.success) {
    const toast = await toastController.create({
      message: 'Часы работы успешно сохранены',
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка при сохранении',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}
</script>

<style scoped>
.business-hours-form {
  width: 100%;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.days-list {
  margin: 0 0 24px 0;
  border-radius: 8px;
  overflow: hidden;
}

.day-item {
  --padding-start: 0;
  --padding-end: 0;
  --inner-padding-end: 0;
}

.day-content {
  width: 100%;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.day-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.day-toggle {
  display: flex;
  align-items: center;
}

.time-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 12px;
  align-items: end;
}

@media (max-width: 576px) {
  .time-inputs {
    grid-template-columns: 1fr;
  }

  .copy-button {
    justify-self: start;
  }
}

.time-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-input-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--ion-color-medium);
}

.time-button {
  --background: var(--ion-color-light);
  --color: var(--ion-color-dark);
  --border-width: 1px;
  --border-style: solid;
  --border-color: var(--ion-color-light-shade);
  --border-radius: 8px;
  --padding-start: 12px;
  --padding-end: 12px;
  height: 44px;
  font-size: 1rem;
  text-transform: none;
  letter-spacing: normal;
  font-weight: 500;
  margin: 0;
}

.copy-button {
  height: 40px;
  margin: 0;
}

.error-message {
  color: var(--ion-color-danger);
  font-size: 0.85rem;
  margin-top: 4px;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

/* Time Picker Modal Styles */
ion-datetime {
  --background: var(--ion-background-color);
}
</style>
