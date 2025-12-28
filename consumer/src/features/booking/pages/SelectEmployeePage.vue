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
      <div v-if="loading" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Content -->
      <div v-else-if="employees.length > 0" class="page-content">
        <h2 class="section-title">Выберите мастера</h2>

        <div class="employees-list">
          <ion-card
            v-for="employee in employees"
            :key="employee.id"
            class="employee-card"
            button
            @click="selectEmployee(employee)"
          >
            <ion-card-content>
              <div class="employee-content">
                <!-- Employee Photo -->
                <div class="employee-photo">
                  <img
                    v-if="employee.photo_url"
                    :src="getFullPhotoUrl(employee.photo_url)"
                    :alt="employee.name"
                    class="photo-image"
                  />
                  <div v-else class="photo-placeholder">
                    <ion-icon :icon="personOutline" size="large"></ion-icon>
                  </div>
                </div>

                <!-- Employee Info -->
                <div class="employee-info">
                  <h3 class="employee-name">{{ employee.name }}</h3>
                  <p v-if="employee.phone" class="employee-phone">
                    <ion-icon :icon="callOutline" class="phone-icon"></ion-icon>
                    {{ employee.phone }}
                  </p>
                </div>

                <ion-icon :icon="chevronForwardOutline" class="arrow-icon"></ion-icon>
              </div>
            </ion-card-content>
          </ion-card>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading" class="empty-state">
        <p>Нет доступных мастеров для выбранной услуги</p>
        <ion-button @click="router.back()">Назад</ion-button>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <ion-button @click="loadEmployees">Повторить</ion-button>
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
  personOutline,
  callOutline,
  chevronForwardOutline,
} from 'ionicons/icons'
import type { Employee } from '@/features/businesses/types'
import { bookingApiService } from '../services/bookingApiService'
import { useBookingStore } from '../stores/bookingStore'
import apiConfig from '@/core/config'

const router = useRouter()
const route = useRoute()
const bookingStore = useBookingStore()

const businessId = ref<number>(parseInt(route.params.businessId as string))
const serviceId = ref<number>(parseInt(route.params.serviceId as string))
const employees = ref<Employee[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

function getFullPhotoUrl(photoUrl?: string): string {
  if (!photoUrl) return ''
  if (photoUrl.startsWith('http')) return photoUrl
  return `${apiConfig.apiBaseUrl.replace('/api/v1', '')}${photoUrl}`
}

async function loadEmployees() {
  loading.value = true
  error.value = null

  try {
    const allEmployees = await bookingApiService.getBusinessEmployees(businessId.value)

    // Filter employees who can perform the selected service
    employees.value = allEmployees.filter(emp =>
      emp.is_active && emp.service_ids.includes(serviceId.value)
    )
  } catch (err: any) {
    console.error('[SelectEmployeePage] Error loading employees:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить мастеров'
  } finally {
    loading.value = false
  }
}

function selectEmployee(employee: Employee) {
  bookingStore.selectEmployee(employee.id)
  router.push(`/booking/select-date/${businessId.value}/${serviceId.value}/${employee.id}`)
}

onMounted(() => {
  loadEmployees()
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

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.employees-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.employee-card {
  margin: 0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.employee-card:active {
  transform: scale(0.98);
}

.employee-card ion-card-content {
  padding: 16px;
}

.employee-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.employee-photo {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0f0f0;
  flex-shrink: 0;
}

.photo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ion-color-medium);
}

.employee-info {
  flex: 1;
  min-width: 0;
}

.employee-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.employee-phone {
  margin: 0;
  font-size: 13px;
  color: var(--ion-color-medium);
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.phone-icon {
  font-size: 14px;
}

.arrow-icon {
  font-size: 20px;
  color: var(--ion-color-medium);
  flex-shrink: 0;
}

.empty-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--ion-color-medium);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.empty-state ion-button,
.error-state ion-button {
  margin-top: 16px;
}
</style>
