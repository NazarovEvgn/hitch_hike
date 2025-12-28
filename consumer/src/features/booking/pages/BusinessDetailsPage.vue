<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-button @click="router.back()" class="back-button">
            <ion-icon slot="icon-only" :icon="arrowBackOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Loading -->
      <div v-if="loading && !business" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Content -->
      <div v-else-if="business" class="page-content">
        <!-- Business Card -->
        <div class="business-card">
          <!-- Logo -->
          <div class="logo-section">
            <div class="logo-wrapper">
              <img
                v-if="business.logo_url"
                :src="getFullLogoUrl(business.logo_url)"
                alt="Logo"
                class="logo-image"
              />
              <div v-else class="logo-placeholder">
                {{ business.name.charAt(0).toUpperCase() }}
              </div>
            </div>
          </div>

          <!-- Business Name -->
          <div class="business-name-display">
            {{ business.name }}
          </div>

          <!-- Business Type -->
          <div class="business-type-display">
            {{ businessTypeLabel(business.business_type) }}
          </div>

          <!-- Address -->
          <div class="business-info-row">
            <ion-icon :icon="locationOutline" class="info-icon"></ion-icon>
            <span>{{ business.address }}</span>
          </div>

          <!-- Phone -->
          <div class="business-info-row">
            <ion-icon :icon="callOutline" class="info-icon"></ion-icon>
            <span>{{ business.phone }}</span>
          </div>
        </div>

        <!-- Services List -->
        <div class="services-section">
          <h2 class="section-title">Выберите услугу</h2>

          <div v-if="loadingServices" class="loading-container">
            <ion-spinner name="crescent"></ion-spinner>
          </div>

          <div v-else-if="services.length === 0" class="empty-state">
            <p>Нет доступных услуг</p>
          </div>

          <div v-else class="services-list">
            <ion-card
              v-for="service in services"
              :key="service.id"
              class="service-card"
              button
              @click="selectService(service)"
            >
              <ion-card-content>
                <div class="service-content">
                  <div class="service-info">
                    <h3 class="service-name">{{ service.name }}</h3>
                    <p v-if="service.description" class="service-description">
                      {{ service.description }}
                    </p>
                    <div class="service-meta">
                      <div class="meta-item">
                        <ion-icon :icon="timeOutline" class="meta-icon"></ion-icon>
                        <span>{{ service.duration_minutes }} мин</span>
                      </div>
                      <div class="meta-item">
                        <ion-icon :icon="cashOutline" class="meta-icon"></ion-icon>
                        <span>{{ formatPrice(service.price_from, service.price_to) }}</span>
                      </div>
                    </div>
                  </div>
                  <ion-icon :icon="chevronForwardOutline" class="arrow-icon"></ion-icon>
                </div>
              </ion-card-content>
            </ion-card>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <ion-button @click="loadData">Повторить</ion-button>
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
  IonSpinner,
  IonCard,
  IonCardContent,
} from '@ionic/vue'
import {
  arrowBackOutline,
  locationOutline,
  callOutline,
  timeOutline,
  cashOutline,
  chevronForwardOutline,
} from 'ionicons/icons'
import type { Business, Service } from '@/features/businesses/types'
import { bookingApiService } from '../services/bookingApiService'
import { useBookingStore } from '../stores/bookingStore'
import apiConfig from '@/core/config'

const router = useRouter()
const route = useRoute()
const bookingStore = useBookingStore()

const businessId = ref<number>(parseInt(route.params.businessId as string))
const business = ref<Business | null>(null)
const services = ref<Service[]>([])
const loading = ref(false)
const loadingServices = ref(false)
const error = ref<string | null>(null)

function getFullLogoUrl(logoUrl?: string): string {
  if (!logoUrl) return ''
  if (logoUrl.startsWith('http')) return logoUrl
  return `${apiConfig.apiBaseUrl.replace('/api/v1', '')}${logoUrl}`
}

function businessTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    car_wash: 'Автомойка',
    auto_repair: 'Автосервис',
    tire_service: 'Шиномонтаж',
    beauty_salon: 'Салон красоты',
  }
  return labels[type] || type
}

function formatPrice(priceFrom: number, priceTo: number): string {
  if (priceFrom === priceTo) {
    return `${priceFrom} ₽`
  }
  return `${priceFrom} - ${priceTo} ₽`
}

async function loadData() {
  loading.value = true
  error.value = null

  try {
    // Load business details
    business.value = await bookingApiService.getBusinessById(businessId.value)

    // Initialize booking with this business
    bookingStore.startBooking(businessId.value)

    // Load services
    await loadServices()
  } catch (err: any) {
    console.error('[BusinessDetailsPage] Error loading data:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

async function loadServices() {
  loadingServices.value = true

  try {
    services.value = await bookingApiService.getBusinessServices(businessId.value)
    // Filter only active services
    services.value = services.value.filter(s => s.is_active)
  } catch (err: any) {
    console.error('[BusinessDetailsPage] Error loading services:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить услуги'
  } finally {
    loadingServices.value = false
  }
}

function selectService(service: Service) {
  bookingStore.selectService(service.id)
  router.push(`/booking/select-employee/${businessId.value}/${service.id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
ion-header ion-toolbar {
  --background: transparent;
  --border-width: 0;
}

.back-button {
  --color: var(--ion-color-primary);
}

ion-content {
  --background: #f5f5f5;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.page-content {
  padding: 16px;
}

/* Business Card */
.business-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.logo-section {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.logo-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 600;
  color: var(--ion-color-primary);
  background: var(--ion-color-primary-tint);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.business-name-display {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.business-type-display {
  font-size: 14px;
  color: var(--ion-color-medium);
  margin-bottom: 16px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.business-info-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: var(--ion-color-dark);
  margin-bottom: 8px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.business-info-row:last-child {
  margin-bottom: 0;
}

.info-icon {
  font-size: 18px;
  color: var(--ion-color-primary);
}

/* Services Section */
.services-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.services-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.service-card {
  margin: 0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.service-card:active {
  transform: scale(0.98);
}

.service-card ion-card-content {
  padding: 16px;
}

.service-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.service-info {
  flex: 1;
}

.service-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.service-description {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--ion-color-medium);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.service-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--ion-color-dark);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.meta-icon {
  font-size: 16px;
  color: var(--ion-color-primary);
}

.arrow-icon {
  font-size: 20px;
  color: var(--ion-color-medium);
}

.empty-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--ion-color-medium);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}
</style>
