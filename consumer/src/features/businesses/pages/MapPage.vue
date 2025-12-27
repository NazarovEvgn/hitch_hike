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

        <!-- Favorites Button -->
        <ion-buttons slot="end">
          <ion-button @click="router.push('/favorites')">
            <ion-icon slot="icon-only" :icon="heartOutline"></ion-icon>
            <ion-badge v-if="favoritesCount > 0" color="danger">{{ favoritesCount }}</ion-badge>
          </ion-button>
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
} from '@ionic/vue'
import {
  heartOutline,
  businessOutline,
  locationOutline,
  callOutline,
  timeOutline,
  closeOutline,
  calendarOutline,
  personCircleOutline,
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
const favoritesCount = ref(0)

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

  // Load favorites count from localStorage
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
  favoritesCount.value = favorites.length
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
</style>
