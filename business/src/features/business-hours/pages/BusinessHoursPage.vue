<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Часы работы</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Back Button -->
      <div class="back-button-container">
        <ion-button fill="clear" size="small" @click="$router.back()">
          <ion-icon slot="start" :icon="arrowBackOutline"></ion-icon>
          Назад
        </ion-button>
      </div>

      <!-- Loading -->
      <div v-if="businessHoursStore.loading && schedules.length === 0" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Schedule Form -->
      <div v-else class="hours-form ion-padding">
        <div class="subtitle">Настройте расписание работы вашего сервиса</div>

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
                  <ion-input
                    v-model="day.openTime"
                    type="time"
                    @ionChange="validateDay(index)"
                  ></ion-input>
                </div>

                <div class="time-input-group">
                  <label>Закрытие</label>
                  <ion-input
                    v-model="day.closeTime"
                    type="time"
                    @ionChange="validateDay(index)"
                  ></ion-input>
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

        <!-- Hints Card -->
        <ion-card class="hints-card">
          <ion-card-content>
            <div class="hints-title">💡 Подсказки</div>
            <ul class="hints-list">
              <li>Настройте часы работы для каждого дня недели</li>
              <li>Используйте кнопку копирования для применения одного расписания ко всем дням</li>
              <li>Время открытия должно быть раньше времени закрытия</li>
              <li>Клиенты смогут записываться только в рабочие часы</li>
            </ul>
          </ion-card-content>
        </ion-card>

        <!-- Back to Home Button -->
        <div class="back-to-home-container">
          <ion-button expand="block" fill="outline" color="medium" @click="$router.push('/dashboard')">
            <ion-icon slot="start" :icon="homeOutline"></ion-icon>
            На главную
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonList,
  IonItem,
  IonToggle,
  IonInput,
  IonButton,
  IonIcon,
  IonCard,
  IonCardContent,
  IonSpinner,
  toastController,
} from '@ionic/vue'
import { copyOutline, arrowBackOutline, homeOutline } from 'ionicons/icons'
import { useBusinessHoursStore } from '../stores/businessHoursStore'
import type { DaySchedule } from '../types'

const businessHoursStore = useBusinessHoursStore()

const schedules = ref<DaySchedule[]>([])
const isSaving = ref(false)

const hasErrors = computed(() => {
  return schedules.value.some(day => day.error !== null)
})

onMounted(async () => {
  schedules.value = await businessHoursStore.fetchBusinessHours()
})

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
.back-button-container {
  padding: 8px 16px;
}

.back-to-home-container {
  padding: 24px 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  padding: 24px;
}

.hours-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
}

.subtitle {
  font-size: 0.9rem;
  color: var(--ion-color-medium);
  margin-bottom: 16px;
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

.time-input-group ion-input {
  --background: var(--ion-color-light);
  --padding-start: 12px;
  --padding-end: 12px;
  border-radius: 8px;
  font-size: 1rem;
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
  margin-bottom: 24px;
}

.hints-card {
  background: var(--ion-color-light);
  box-shadow: none;
}

.hints-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--ion-color-primary);
}

.hints-list {
  margin: 0;
  padding-left: 20px;
  font-size: 0.85rem;
  color: var(--ion-color-medium);
}

.hints-list li {
  margin-bottom: 4px;
}
</style>
