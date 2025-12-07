<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-menu-button></ion-menu-button>
        </ion-buttons>
        <ion-title>Онлайн-записи</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="fetchBookings()">
            <ion-icon slot="icon-only" :icon="refreshOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Filter -->
      <div class="filter-container ion-padding">
        <ion-segment v-model="selectedStatus" @ion-change="handleFilterChange">
          <ion-segment-button value="all">
            <ion-label>Все</ion-label>
          </ion-segment-button>
          <ion-segment-button value="pending">
            <ion-label>Ожидает</ion-label>
          </ion-segment-button>
          <ion-segment-button value="confirmed">
            <ion-label>Подтверждено</ion-label>
          </ion-segment-button>
          <ion-segment-button value="completed">
            <ion-label>Завершено</ion-label>
          </ion-segment-button>
        </ion-segment>
      </div>

      <!-- Loading -->
      <div v-if="bookingsStore.loading && bookingsStore.bookings.length === 0" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Empty State -->
      <div v-else-if="!bookingsStore.loading && bookingsStore.bookings.length === 0" class="empty-state">
        <ion-icon :icon="calendarOutline" size="large" color="medium"></ion-icon>
        <p>Нет записей</p>
      </div>

      <!-- Bookings List -->
      <ion-list v-else>
        <ion-item-sliding v-for="booking in bookingsStore.bookings" :key="booking.id">
          <ion-item button @click="viewDetails(booking)">
            <div class="booking-card">
              <!-- Header -->
              <div class="booking-header">
                <div class="booking-client">
                  <h3>{{ booking.client_name }}</h3>
                  <p class="phone">{{ booking.client_phone }}</p>
                </div>
                <ion-badge :color="getStatusColor(booking.status)">
                  {{ getStatusLabel(booking.status) }}
                </ion-badge>
              </div>

              <!-- Details -->
              <div class="booking-details">
                <div class="detail-row">
                  <ion-icon :icon="calendarOutline" color="primary"></ion-icon>
                  <span>{{ formatDate(booking.booking_date) }}</span>
                  <ion-icon :icon="timeOutline" color="primary" class="ml-2"></ion-icon>
                  <span>{{ booking.booking_time }}</span>
                </div>

                <div v-if="booking.service" class="detail-row">
                  <ion-icon :icon="pricetagOutline" color="primary"></ion-icon>
                  <span>{{ booking.service.name }}</span>
                </div>

                <div v-if="booking.came_through_app" class="detail-row">
                  <ion-icon :icon="phonePortraitOutline" color="success"></ion-icon>
                  <span class="text-success">Через приложение</span>
                </div>
              </div>
            </div>
          </ion-item>

          <ion-item-options>
            <ion-item-option
              v-if="booking.status === 'pending'"
              color="success"
              @click="updateStatus(booking, 'confirmed')"
            >
              <ion-icon slot="icon-only" :icon="checkmarkOutline"></ion-icon>
            </ion-item-option>
            <ion-item-option
              v-if="booking.status === 'confirmed'"
              color="primary"
              @click="updateStatus(booking, 'completed')"
            >
              <ion-icon slot="icon-only" :icon="checkmarkDoneOutline"></ion-icon>
            </ion-item-option>
            <ion-item-option
              v-if="['pending', 'confirmed'].includes(booking.status)"
              color="danger"
              @click="updateStatus(booking, 'cancelled')"
            >
              <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
            </ion-item-option>
          </ion-item-options>
        </ion-item-sliding>
      </ion-list>
    </ion-content>

    <!-- Details Modal -->
    <BookingDetailsModal
      :is-open="isDetailsModalOpen"
      :booking="selectedBooking"
      @close="closeDetailsModal"
      @status-update="handleStatusUpdate"
    />
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
  IonButton,
  IonTitle,
  IonContent,
  IonSegment,
  IonSegmentButton,
  IonLabel,
  IonList,
  IonItem,
  IonItemSliding,
  IonItemOptions,
  IonItemOption,
  IonIcon,
  IonBadge,
  IonSpinner,
  toastController,
} from '@ionic/vue'
import {
  refreshOutline,
  calendarOutline,
  timeOutline,
  pricetagOutline,
  phonePortraitOutline,
  checkmarkOutline,
  checkmarkDoneOutline,
  closeOutline,
} from 'ionicons/icons'
import { useBookingsStore } from '../stores/bookingsStore'
import BookingDetailsModal from '../components/BookingDetailsModal.vue'
import type { Booking, BookingStatus } from '../types'

const bookingsStore = useBookingsStore()
const selectedStatus = ref('all')
const isDetailsModalOpen = ref(false)
const selectedBooking = ref<Booking | null>(null)

onMounted(async () => {
  await fetchBookings()
})

async function fetchBookings() {
  const filters = selectedStatus.value !== 'all' ? { status: selectedStatus.value as BookingStatus } : {}
  await bookingsStore.fetchBookings(filters)
}

function handleFilterChange() {
  fetchBookings()
}

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

function viewDetails(booking: Booking) {
  selectedBooking.value = booking
  isDetailsModalOpen.value = true
}

function closeDetailsModal() {
  isDetailsModalOpen.value = false
  selectedBooking.value = null
}

async function updateStatus(booking: Booking, newStatus: BookingStatus) {
  const result = await bookingsStore.updateBookingStatus(booking.id, newStatus)

  if (result.success) {
    const toast = await toastController.create({
      message: `Статус изменен на "${getStatusLabel(newStatus)}"`,
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка изменения статуса',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}

async function handleStatusUpdate(bookingId: number, newStatus: BookingStatus) {
  await updateStatus(bookingsStore.bookings.find(b => b.id === bookingId)!, newStatus)
  closeDetailsModal()
}
</script>

<style scoped>
.filter-container {
  padding: 12px 16px;
  background: var(--ion-color-light);
}

.loading-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  padding: 24px;
}

.empty-state p {
  color: var(--ion-color-medium);
  margin: 0;
}

.empty-state ion-icon {
  font-size: 64px;
}

.booking-card {
  width: 100%;
  padding: 12px 0;
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.booking-client h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.booking-client .phone {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
}

.booking-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
}

.detail-row ion-icon {
  font-size: 18px;
}

.ml-2 {
  margin-left: 8px;
}

.text-success {
  color: var(--ion-color-success);
  font-weight: 500;
}
</style>
