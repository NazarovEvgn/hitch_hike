<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>Lets</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="router.push('/favorites')">
            <ion-icon slot="icon-only" :icon="heartOutline"></ion-icon>
            <ion-badge v-if="favoritesCount > 0" color="danger">{{ favoritesCount }}</ion-badge>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Filter Buttons -->
      <div class="filter-panel">
        <ion-segment v-model="selectedType" @ionChange="handleFilterChange">
          <ion-segment-button value="">
            <ion-label>Все</ion-label>
          </ion-segment-button>
          <ion-segment-button value="car_wash">
            <ion-icon :icon="carSportOutline"></ion-icon>
            <ion-label>Автомойки</ion-label>
          </ion-segment-button>
          <ion-segment-button value="auto_repair">
            <ion-icon :icon="buildOutline"></ion-icon>
            <ion-label>Ремонт</ion-label>
          </ion-segment-button>
          <ion-segment-button value="tire_service">
            <ion-icon :icon="ellipseOutline"></ion-icon>
            <ion-label>Шиномонтаж</ion-label>
          </ion-segment-button>
          <ion-segment-button value="beauty_salon">
            <ion-icon :icon="sparklesOutline"></ion-icon>
            <ion-label>Салоны</ion-label>
          </ion-segment-button>
        </ion-segment>
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
  IonSegment,
  IonSegmentButton,
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
  carSportOutline,
  buildOutline,
  ellipseOutline,
  sparklesOutline,
  businessOutline,
  locationOutline,
  callOutline,
  timeOutline,
  closeOutline,
  calendarOutline,
} from 'ionicons/icons'
import { useBusinessesStore } from '../stores/businessesStore'
import type { Business, BusinessType, BusinessStatus } from '../types'

const router = useRouter()
const businessesStore = useBusinessesStore()

const selectedType = ref<BusinessType | ''>('')
const selectedBusiness = ref<Business | null>(null)
const favoritesCount = ref(0)

const filteredBusinesses = computed(() => {
  if (!selectedType.value) return businessesStore.businesses
  return businessesStore.filterByType(selectedType.value as BusinessType)
})

onMounted(async () => {
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

function handleFilterChange() {
  // Filter is reactive via computed
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
.filter-panel {
  padding: 12px;
  background: var(--ion-color-light);
  position: sticky;
  top: 0;
  z-index: 10;
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
