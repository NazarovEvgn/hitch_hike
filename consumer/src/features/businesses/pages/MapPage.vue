<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <!-- Client Profile -->
        <div slot="start" class="profile-header" @click="router.push('/profile')">
          <div class="avatar-small">
            <img
              v-if="profileStore.profile?.avatar_url"
              :src="getFullAvatarUrl(profileStore.profile.avatar_url)"
              alt="Avatar"
            />
            <ion-icon v-else :icon="personCircleOutline"></ion-icon>
          </div>
          <div class="profile-info">
            <div class="profile-name">{{ profileStore.profile?.name || 'Гость' }}</div>
            <div class="profile-link">Ваши настройки ></div>
          </div>
        </div>

        <!-- Notifications Button -->
        <ion-buttons slot="end">
          <div class="notifications-button-wrapper">
            <ion-button id="notifications-trigger">
              <ion-icon slot="icon-only" :icon="notificationsOutline" class="notifications-icon"></ion-icon>
            </ion-button>
            <ion-badge v-if="unreadNotifications > 0" color="danger" class="notifications-badge">{{ unreadNotifications }}</ion-badge>
          </div>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Современное поле поиска -->
      <div class="search-panel">
        <ion-searchbar
          v-model="searchQuery"
          placeholder="Поиск по названию или адресу..."
          :debounce="300"
          animated
          show-clear-button="focus"
          class="custom-searchbar"
        ></ion-searchbar>
      </div>

      <!-- Loading -->
      <div v-if="businessesStore.loading" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredBusinesses.length === 0" class="empty-state">
        <ion-icon :icon="businessOutline" size="large" color="medium"></ion-icon>
        <p>Нет доступных бизнесов</p>
      </div>

      <!-- Business List -->
      <ion-list v-else>
        <ion-item
          v-for="business in filteredBusinesses"
          :key="business.id"
          button
          @click="selectBusiness(business)"
        >
          <div class="business-card">
            <div class="business-header">
              <div class="business-info">
                <h3>{{ business.name }}</h3>
                <p class="business-type">{{ businessTypeLabel(business.business_type) }}</p>
              </div>
              <ion-badge :color="statusColor(business.status?.status || 'available')">
                {{ statusLabel(business.status?.status || 'available') }}
              </ion-badge>
            </div>

            <div class="business-details">
              <div class="detail-row">
                <ion-icon :icon="locationOutline" color="medium"></ion-icon>
                <span>{{ business.address }}</span>
              </div>
              <div class="detail-row">
                <ion-icon :icon="callOutline" color="medium"></ion-icon>
                <span>{{ business.phone }}</span>
              </div>
              <div v-if="business.status" class="detail-row">
                <ion-icon :icon="timeOutline" color="medium"></ion-icon>
                <span>Ожидание: ~{{ business.status.estimated_wait_minutes }} мин</span>
              </div>
            </div>
          </div>
        </ion-item>
      </ion-list>
    </ion-content>

    <!-- Notifications Popover -->
    <ion-popover trigger="notifications-trigger" :dismiss-on-select="true">
      <ion-content class="notifications-popover">
        <div class="notifications-header">
          <h3>Уведомления</h3>
          <ion-button
            v-if="notifications.length > 0"
            fill="clear"
            size="small"
            @click="markAllAsRead"
          >
            Отметить все
          </ion-button>
        </div>

        <!-- Notifications List -->
        <ion-list v-if="notifications.length > 0" class="notifications-list">
          <ion-item
            v-for="notification in notifications"
            :key="notification.id"
            :class="{ 'unread': !notification.read }"
            button
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-content">
              <div class="notification-icon" :class="`type-${notification.type}`">
                <ion-icon
                  :icon="getNotificationIcon(notification.type)"
                ></ion-icon>
              </div>
              <div class="notification-text">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-message">{{ notification.message }}</div>
                <div class="notification-time">{{ formatTime(notification.time) }}</div>
              </div>
            </div>
          </ion-item>
        </ion-list>

        <!-- Empty State -->
        <div v-else class="notifications-empty">
          <ion-icon :icon="notificationsOffOutline" size="large"></ion-icon>
          <p>Нет уведомлений</p>
        </div>
      </ion-content>
    </ion-popover>

    <!-- Business Details Modal -->
    <ion-modal :is-open="!!selectedBusiness" @did-dismiss="selectedBusiness = null">
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>{{ selectedBusiness?.name }}</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="selectedBusiness = null">
              <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
            </ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>

      <ion-content v-if="selectedBusiness" class="ion-padding">
        <ion-card>
          <ion-card-content>
            <div class="modal-detail-row">
              <strong>Тип:</strong>
              <span>{{ businessTypeLabel(selectedBusiness.business_type) }}</span>
            </div>
            <div class="modal-detail-row">
              <strong>Статус:</strong>
              <ion-badge :color="statusColor(selectedBusiness.status?.status || 'available')">
                {{ statusLabel(selectedBusiness.status?.status || 'available') }}
              </ion-badge>
            </div>
            <div class="modal-detail-row">
              <strong>Адрес:</strong>
              <span>{{ selectedBusiness.address }}</span>
            </div>
            <div class="modal-detail-row">
              <strong>Телефон:</strong>
              <span>{{ selectedBusiness.phone }}</span>
            </div>
            <div v-if="selectedBusiness.status" class="modal-detail-row">
              <strong>Ожидание:</strong>
              <span>~{{ selectedBusiness.status.estimated_wait_minutes }} минут</span>
            </div>
            <div v-if="selectedBusiness.description" class="modal-detail-row">
              <strong>Описание:</strong>
              <p>{{ selectedBusiness.description }}</p>
            </div>
          </ion-card-content>
        </ion-card>

        <div class="action-buttons">
          <ion-button expand="block" color="primary" @click="call(selectedBusiness.phone)">
            <ion-icon slot="start" :icon="callOutline"></ion-icon>
            Позвонить
          </ion-button>
          <ion-button expand="block" color="secondary" @click="bookService(selectedBusiness)">
            <ion-icon slot="start" :icon="calendarOutline"></ion-icon>
            Записаться
          </ion-button>
        </div>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonSearchbar,
  IonLabel,
  IonList,
  IonItem,
  IonIcon,
  IonBadge,
  IonSpinner,
  IonModal,
  IonCard,
  IonCardContent,
  IonPopover,
} from '@ionic/vue'
import {
  notificationsOutline,
  notificationsOffOutline,
  businessOutline,
  locationOutline,
  callOutline,
  timeOutline,
  closeOutline,
  calendarOutline,
  personCircleOutline,
  checkmarkCircleOutline,
  alertCircleOutline,
  informationCircleOutline,
} from 'ionicons/icons'
import { useBusinessesStore } from '../stores/businessesStore'
import { useProfileStore } from '@/features/profile/stores/profileStore'
import type { Business, BusinessType, BusinessStatus } from '../types'
import { API_BASE_URL } from '@/core/config'

const router = useRouter()
const businessesStore = useBusinessesStore()
const profileStore = useProfileStore()

const searchQuery = ref('')
const selectedBusiness = ref<Business | null>(null)

// Notifications state
interface Notification {
  id: number
  type: 'success' | 'info' | 'warning'
  title: string
  message: string
  time: Date
  read: boolean
}

const notifications = ref<Notification[]>([
  {
    id: 1,
    type: 'success',
    title: 'Запись подтверждена',
    message: 'Ваша запись на 15:00 успешно подтверждена',
    time: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
    read: false,
  },
  {
    id: 2,
    type: 'info',
    title: 'Напоминание',
    message: 'Через 1 час ваша запись в "Автомойка №1"',
    time: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    read: false,
  },
  {
    id: 3,
    type: 'warning',
    title: 'Изменение времени',
    message: 'Время вашей записи изменено на 16:00',
    time: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    read: true,
  },
])

const unreadNotifications = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const filteredBusinesses = computed(() => {
  let businesses = businessesStore.businesses

  // Фильтрация по поисковому запросу
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    businesses = businesses.filter(
      (b) =>
        b.name.toLowerCase().includes(query) ||
        b.address.toLowerCase().includes(query) ||
        businessTypeLabel(b.business_type).toLowerCase().includes(query)
    )
  }

  return businesses
})

onMounted(async () => {
  // Load user profile
  await profileStore.fetchProfile()

  // Load businesses near Tyumen center
  await businessesStore.fetchNearby({
    latitude: 57.1522,
    longitude: 65.5343,
    radius_km: 10,
  })
})

function getFullAvatarUrl(avatarUrl: string | null): string {
  if (!avatarUrl) return ''
  // Remove /api/v1 from base URL and append avatar URL
  const baseUrl = API_BASE_URL.replace('/api/v1', '')
  return `${baseUrl}${avatarUrl}`
}

function selectBusiness(business: Business) {
  selectedBusiness.value = business
}

function businessTypeLabel(type: BusinessType): string {
  const labels = {
    car_wash: 'Автомойка',
    auto_repair: 'Автосервис',
    tire_service: 'Шиномонтаж',
    beauty_salon: 'Салон красоты',
  }
  return labels[type] || type
}

function statusLabel(status: BusinessStatus): string {
  const labels = {
    available: 'Свободно',
    busy: 'Занято',
    very_busy: 'Очень загружено',
  }
  return labels[status] || status
}

function statusColor(status: BusinessStatus): string {
  const colors = {
    available: 'success',
    busy: 'warning',
    very_busy: 'danger',
  }
  return colors[status] || 'medium'
}

function call(phone: string) {
  window.location.href = `tel:${phone}`
}

function bookService(business: Business) {
  // TODO: Open booking dialog
  console.log('Book service for:', business.name)
  selectedBusiness.value = null
}

function getNotificationIcon(type: string) {
  switch (type) {
    case 'success':
      return checkmarkCircleOutline
    case 'warning':
      return alertCircleOutline
    case 'info':
    default:
      return informationCircleOutline
  }
}

function formatTime(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) {
    return `${diffMins} мин назад`
  } else if (diffHours < 24) {
    return `${diffHours} ч назад`
  } else if (diffDays === 1) {
    return 'Вчера'
  } else if (diffDays < 7) {
    return `${diffDays} дн назад`
  } else {
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  }
}

function handleNotificationClick(notification: Notification) {
  // Mark as read
  notification.read = true

  // TODO: Handle notification action (navigate to booking details, etc.)
  console.log('Notification clicked:', notification)
}

function markAllAsRead() {
  notifications.value.forEach(n => n.read = true)
}
</script>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.profile-header:hover {
  opacity: 0.8;
}

.avatar-small {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-small ion-icon {
  font-size: 40px;
  color: white;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profile-name {
  color: white;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.2;
}

.profile-link {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  line-height: 1.2;
}

/* Notifications Button - iOS Style */
.notifications-button-wrapper {
  position: relative;
  display: inline-block;
}

.notifications-icon {
  font-size: 28px !important;
  color: white;
}

.notifications-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FF3B30;
  color: white;
  border: 2px solid var(--ion-color-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  pointer-events: none;
}

.search-panel {
  padding: 8px 16px;
  background: var(--ion-background-color);
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.custom-searchbar {
  --background: #ffffff;
  --border-radius: 12px;
  --box-shadow: 0 2px 12px rgba(138, 43, 226, 0.12);
  --placeholder-color: #92949c;
  --icon-color: #8A2BE2;
  --clear-button-color: #8A2BE2;
  padding: 0;
}

.custom-searchbar::part(icon) {
  color: var(--ion-color-primary);
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

.business-card {
  width: 100%;
  padding: 12px 0;
}

.business-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.business-info h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.business-type {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
}

.business-details {
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

.modal-detail-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.modal-detail-row strong {
  color: var(--ion-color-medium);
  font-size: 0.9rem;
}

.modal-detail-row p {
  margin: 4px 0 0 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

/* Notifications Popover */
.notifications-popover {
  --width: 360px;
  --max-height: 500px;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--ion-color-light);
}

.notifications-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.notifications-list {
  padding: 0;
}

.notifications-list ion-item {
  --padding-start: 16px;
  --padding-end: 16px;
  --inner-padding-end: 0;
  --min-height: 80px;
  border-bottom: 1px solid var(--ion-color-light);
}

.notifications-list ion-item.unread {
  --background: rgba(138, 43, 226, 0.05);
}

.notification-content {
  display: flex;
  gap: 12px;
  width: 100%;
  padding: 8px 0;
}

.notification-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon ion-icon {
  font-size: 24px;
}

.notification-icon.type-success {
  background: rgba(45, 211, 111, 0.15);
  color: var(--ion-color-success);
}

.notification-icon.type-info {
  background: rgba(61, 194, 255, 0.15);
  color: var(--ion-color-secondary);
}

.notification-icon.type-warning {
  background: rgba(255, 196, 9, 0.15);
  color: var(--ion-color-warning);
}

.notification-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notification-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ion-color-dark);
  line-height: 1.3;
}

.notification-message {
  font-size: 14px;
  color: var(--ion-color-medium);
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: var(--ion-color-medium);
  margin-top: 2px;
}

.notifications-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 16px;
}

.notifications-empty ion-icon {
  font-size: 64px;
  color: var(--ion-color-medium);
  opacity: 0.5;
}

.notifications-empty p {
  margin: 0;
  color: var(--ion-color-medium);
  font-size: 16px;
}
</style>
