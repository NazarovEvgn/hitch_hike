<template>
  <ion-modal :is-open="isOpen" @did-dismiss="$emit('close')">
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Детали бронирования</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="$emit('close')">
            <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding" v-if="booking">
      <!-- Details List -->
      <ion-list>
        <ion-item lines="none">
          <ion-label>
            <p>Дата и время</p>
            <h2>{{ formatDate(booking.booking_date) }}, {{ booking.booking_time }}</h2>
          </ion-label>
        </ion-item>

        <ion-item lines="none">
          <ion-label>
            <p>Клиент</p>
            <h2>{{ booking.client_name }}</h2>
            <p>{{ booking.client_phone }}</p>
          </ion-label>
        </ion-item>

        <ion-item lines="none" v-if="booking.service">
          <ion-label>
            <p>Услуга</p>
            <h2>{{ booking.service.name }}</h2>
          </ion-label>
        </ion-item>

        <ion-item lines="none">
          <ion-label>
            <p>Статус</p>
            <ion-badge :color="getStatusColor(booking.status)">
              {{ getStatusLabel(booking.status) }}
            </ion-badge>
          </ion-label>
        </ion-item>

        <ion-item lines="none" v-if="booking.notes">
          <ion-label>
            <p>Примечания</p>
            <p>{{ booking.notes }}</p>
          </ion-label>
        </ion-item>

        <ion-item lines="none">
          <ion-label>
            <p>Источник</p>
            <div class="source-info">
              <ion-icon
                :icon="booking.came_through_app ? phonePortraitOutline : callOutline"
                :color="booking.came_through_app ? 'success' : 'medium'"
              ></ion-icon>
              <span>{{ booking.came_through_app ? 'Через приложение' : 'Телефон/другое' }}</span>
            </div>
          </ion-label>
        </ion-item>
      </ion-list>

      <!-- Status Update Actions -->
      <div class="actions-section" v-if="canUpdateStatus">
        <h3>Изменить статус:</h3>
        <div class="action-buttons">
          <ion-button
            v-if="booking.status === 'pending'"
            expand="block"
            color="success"
            @click="handleStatusUpdate('confirmed')"
          >
            <ion-icon slot="start" :icon="checkmarkOutline"></ion-icon>
            Подтвердить
          </ion-button>

          <ion-button
            v-if="booking.status === 'confirmed'"
            expand="block"
            color="primary"
            @click="handleStatusUpdate('completed')"
          >
            <ion-icon slot="start" :icon="checkmarkDoneOutline"></ion-icon>
            Завершить
          </ion-button>

          <ion-button
            v-if="['pending', 'confirmed'].includes(booking.status)"
            expand="block"
            color="danger"
            @click="handleStatusUpdate('cancelled')"
          >
            <ion-icon slot="start" :icon="closeOutline"></ion-icon>
            Отменить
          </ion-button>
        </div>
      </div>
    </ion-content>
  </ion-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonBadge,
  IonIcon,
} from '@ionic/vue'
import {
  closeOutline,
  phonePortraitOutline,
  callOutline,
  checkmarkOutline,
  checkmarkDoneOutline,
} from 'ionicons/icons'
import type { Booking, BookingStatus } from '../types'

interface Props {
  isOpen: boolean
  booking: Booking | null
}

interface Emits {
  (e: 'close'): void
  (e: 'status-update', bookingId: number, newStatus: BookingStatus): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const canUpdateStatus = computed(() => {
  return props.booking && ['pending', 'confirmed'].includes(props.booking.status)
})

function getStatusColor(status: BookingStatus): string {
  const colors = {
    pending: 'warning',
    confirmed: 'primary',
    completed: 'success',
    cancelled: 'danger',
  }
  return colors[status] || 'medium'
}

function getStatusLabel(status: BookingStatus): string {
  const labels = {
    pending: 'Ожидает',
    confirmed: 'Подтверждено',
    completed: 'Завершено',
    cancelled: 'Отменено',
  }
  return labels[status] || status
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function handleStatusUpdate(newStatus: BookingStatus) {
  if (props.booking) {
    emit('status-update', props.booking.id, newStatus)
  }
}
</script>

<style scoped>
.source-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.source-info ion-icon {
  font-size: 20px;
}

.actions-section {
  margin-top: 24px;
  padding: 16px;
}

.actions-section h3 {
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
