<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-menu-button></ion-menu-button>
        </ion-buttons>
        <ion-title>Обновление статуса</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <!-- Status Selection Card -->
      <ion-card>
        <ion-card-header>
          <ion-card-title>Выберите текущий статус</ion-card-title>
        </ion-card-header>

        <ion-card-content>
          <!-- Status Buttons -->
          <div class="status-buttons">
            <button
              v-for="option in statusOptions"
              :key="option.value"
              class="status-button"
              :class="{ active: selectedStatus === option.value }"
              :style="{ '--button-color': option.color }"
              @click="selectedStatus = option.value"
            >
              <div class="status-emoji">{{ option.emoji }}</div>
              <div class="status-label">{{ option.label }}</div>
              <div class="status-description">{{ option.description }}</div>
            </button>
          </div>

          <!-- Wait Time Input -->
          <ion-item lines="none" class="ion-margin-top">
            <ion-label position="stacked">Примерное время ожидания (минуты)</ion-label>
            <ion-input
              v-model.number="waitMinutes"
              type="number"
              min="0"
              placeholder="0"
            ></ion-input>
          </ion-item>

          <!-- Update Button -->
          <ion-button
            expand="block"
            size="large"
            class="ion-margin-top"
            @click="handleUpdateStatus"
            :disabled="statusStore.loading"
          >
            <ion-spinner v-if="statusStore.loading" name="crescent"></ion-spinner>
            <span v-else>Обновить статус</span>
          </ion-button>
        </ion-card-content>
      </ion-card>

      <!-- History Card (Placeholder) -->
      <ion-card>
        <ion-card-header>
          <ion-card-title>История обновлений</ion-card-title>
        </ion-card-header>

        <ion-card-content>
          <p class="ion-text-center text-secondary">
            Скоро будет доступна история обновлений статуса
          </p>
        </ion-card-content>
      </ion-card>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonMenuButton,
  IonTitle,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonSpinner,
  toastController,
} from '@ionic/vue'
import { useStatusStore } from '../stores/statusStore'
import type { BusinessStatus } from '../types'

const statusStore = useStatusStore()

// Status options
const statusOptions = [
  {
    value: 'available' as BusinessStatus,
    label: 'Доступен',
    emoji: '🟢',
    description: '0-15 мин',
    color: '#98EA14', // Brand green
  },
  {
    value: 'busy' as BusinessStatus,
    label: 'Занят',
    emoji: '🟡',
    description: '15-30 мин',
    color: '#ffc409', // Ionic warning yellow
  },
  {
    value: 'very_busy' as BusinessStatus,
    label: 'Очень занят',
    emoji: '🟠',
    description: '30+ мин',
    color: '#eb445a', // Ionic danger red
  },
]

// Form state
const selectedStatus = ref<BusinessStatus>('available')
const waitMinutes = ref(0)

// Load current status on mount
onMounted(async () => {
  await statusStore.fetchCurrentStatus()

  // Pre-fill form with current values
  if (statusStore.currentStatus) {
    selectedStatus.value = statusStore.currentStatus.status
    waitMinutes.value = statusStore.currentStatus.estimated_wait_minutes
  }
})

// Handle status update
async function handleUpdateStatus() {
  const result = await statusStore.updateStatus({
    status: selectedStatus.value,
    estimated_wait_minutes: waitMinutes.value,
  })

  if (result.success) {
    const toast = await toastController.create({
      message: 'Статус успешно обновлен!',
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка при обновлении статуса',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}
</script>

<style scoped>
/* Status Buttons Grid */
.status-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 1.5rem;
}

.status-button {
  background: var(--ion-color-light);
  border: 2px solid var(--ion-color-light-shade);
  border-radius: 12px;
  padding: 1.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.status-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-button.active {
  background: var(--button-color);
  border-color: var(--button-color);
  color: white;
}

.status-button.active .status-description {
  color: rgba(255, 255, 255, 0.9);
}

.status-emoji {
  font-size: 2.5rem;
  margin-bottom: 4px;
}

.status-label {
  font-size: 1.1rem;
  font-weight: 600;
}

.status-description {
  font-size: 0.85rem;
  color: var(--ion-color-medium);
}

/* Input Items */
ion-item {
  --background: var(--ion-color-light);
  --border-radius: 8px;
  --padding-start: 16px;
  --padding-end: 16px;
  margin-bottom: 12px;
}

ion-label {
  font-weight: 500;
  margin-bottom: 8px;
}

/* Secondary Text */
.text-secondary {
  color: var(--ion-color-medium);
  font-size: 0.9rem;
}

/* Responsive: Stack buttons on mobile */
@media (max-width: 576px) {
  .status-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
