<template>
  <ion-page>
    <AppHeader />

    <ion-content :fullscreen="true">
      <PageNavigation page-title="Услуги" />

      <div class="content-container">
        <!-- Loading State -->
        <div v-if="servicesStore.loading && servicesStore.services.length === 0" class="loading-container">
          <ion-spinner name="crescent"></ion-spinner>
        </div>

        <!-- Empty State -->
        <div v-else-if="!servicesStore.loading && servicesStore.services.length === 0" class="empty-state">
          <ion-icon :icon="pricetagOutline" size="large" color="medium"></ion-icon>
          <p>Нет добавленных услуг</p>
          <ion-button @click="openCreateModal">Добавить первую услугу</ion-button>
        </div>

        <!-- Services Section -->
        <div v-else>
          <!-- Section Header -->
          <div class="section-header">
            <h2 class="section-title">Текущие услуги</h2>
            <ion-button fill="clear" @click="openCreateModal" class="add-service-button">
              <ion-icon slot="start" :icon="addOutline"></ion-icon>
              Добавить услугу
            </ion-button>
          </div>

          <!-- Services List -->
          <ion-list>
        <ion-item-sliding v-for="service in servicesStore.services" :key="service.id">
          <ion-item button @click="openEditModal(service)">
            <div class="service-card">
              <!-- Service Photo -->
              <div v-if="service.photo_url" class="service-photo">
                <img :src="getPhotoUrl(service.photo_url)" :alt="service.name" />
              </div>
              <div v-else class="service-photo-placeholder">
                <ion-icon :icon="imageOutline" size="large"></ion-icon>
                <span>Фото услуги</span>
              </div>

              <!-- Service Header -->
              <div class="service-header">
                <div class="service-info">
                  <h3>{{ service.name }}</h3>
                </div>
                <div class="service-toggle" @click.stop>
                  <ion-toggle
                    :checked="service.is_active"
                    @ion-change="toggleActive(service.id)"
                    color="success"
                  ></ion-toggle>
                </div>
              </div>

              <!-- Service Description -->
              <p v-if="service.description" class="service-description">
                {{ service.description }}
              </p>

              <!-- Service Details -->
              <div class="service-details">
                <div class="detail-item">
                  <ion-icon :icon="cashOutline" color="primary"></ion-icon>
                  <span class="detail-value">{{ formatPriceRange(service.price_from, service.price_to) }}</span>
                </div>
                <div class="detail-item">
                  <ion-icon :icon="timeOutline" color="primary"></ion-icon>
                  <span class="detail-value">{{ service.duration_minutes }} мин</span>
                </div>
                <div class="detail-item">
                  <ion-badge :color="service.is_active ? 'success' : 'medium'">
                    {{ service.is_active ? 'Активна' : 'Неактивна' }}
                  </ion-badge>
                </div>
              </div>
            </div>
          </ion-item>

          <ion-item-options>
            <ion-item-option color="primary" @click="openEditModal(service)">
              <ion-icon slot="icon-only" :icon="createOutline"></ion-icon>
            </ion-item-option>
            <ion-item-option color="danger" @click="confirmDelete(service)">
              <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
            </ion-item-option>
          </ion-item-options>
        </ion-item-sliding>
          </ion-list>
        </div>

        <!-- Back to Home Button -->
        <div class="back-to-home-container">
          <ion-button expand="block" fill="outline" color="medium" @click="$router.push('/dashboard')">
            <ion-icon slot="start" :icon="homeOutline"></ion-icon>
            На главную
          </ion-button>
        </div>
      </div>
    </ion-content>

    <!-- Service Form Modal -->
    <ServiceFormModal
      :is-open="isModalOpen"
      :service="selectedService"
      @close="closeModal"
      @save="handleSave"
      @delete="handleDeleteFromModal"
    />
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  IonPage,
  IonContent,
  IonList,
  IonItem,
  IonItemSliding,
  IonItemOptions,
  IonItemOption,
  IonIcon,
  IonToggle,
  IonBadge,
  IonSpinner,
  IonButton,
  alertController,
  toastController,
} from '@ionic/vue'
import {
  addOutline,
  pricetagOutline,
  cashOutline,
  timeOutline,
  createOutline,
  trashOutline,
  homeOutline,
  imageOutline,
} from 'ionicons/icons'
import { useServicesStore } from '../stores/servicesStore'
import ServiceFormModal from '../components/ServiceFormModal.vue'
import type { Service, ServiceFormData } from '../types'
import AppHeader from '@/shared/components/AppHeader.vue'
import PageNavigation from '@/shared/components/PageNavigation.vue'

const servicesStore = useServicesStore()
const isModalOpen = ref(false)
const selectedService = ref<Service | null>(null)

// Load services on mount
onMounted(async () => {
  await servicesStore.fetchServices()
})

// Format price range to RUB
function formatPriceRange(priceFrom: number, priceTo: number): string {
  // Handle NaN or undefined values
  if (!priceFrom && priceFrom !== 0) priceFrom = 0
  if (!priceTo && priceTo !== 0) priceTo = 0

  const formatter = new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
  })

  if (priceFrom === priceTo) {
    return formatter.format(priceFrom)
  }

  return `${formatter.format(priceFrom)} - ${formatter.format(priceTo)}`
}

// Get full photo URL
function getPhotoUrl(photoUrl: string | null): string {
  if (!photoUrl) return ''
  // If it's already a full URL, return as is
  if (photoUrl.startsWith('http')) return photoUrl
  // Otherwise prepend API base URL
  return `${import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')}${photoUrl}`
}

// Open create modal
function openCreateModal() {
  selectedService.value = null
  isModalOpen.value = true
}

// Open edit modal
function openEditModal(service: Service) {
  selectedService.value = service
  isModalOpen.value = true
}

// Close modal
function closeModal() {
  isModalOpen.value = false
  selectedService.value = null
}

// Handle save (create or update)
async function handleSave(formData: ServiceFormData) {
  let result

  if (selectedService.value) {
    // Update existing service
    result = await servicesStore.updateService(selectedService.value.id, formData)
  } else {
    // Create new service
    result = await servicesStore.createService(formData)
  }

  if (result.success) {
    const toast = await toastController.create({
      message: selectedService.value ? 'Услуга обновлена' : 'Услуга создана',
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
    closeModal()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка сохранения',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}

// Toggle service active status
async function toggleActive(id: number) {
  const result = await servicesStore.toggleServiceActive(id)

  if (!result.success) {
    const toast = await toastController.create({
      message: result.error || 'Ошибка изменения статуса',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}

// Confirm delete
async function confirmDelete(service: Service) {
  const alert = await alertController.create({
    header: 'Удаление услуги',
    message: `Вы уверены, что хотите удалить "${service.name}"?`,
    buttons: [
      {
        text: 'Отмена',
        role: 'cancel',
      },
      {
        text: 'Удалить',
        role: 'destructive',
        handler: () => handleDelete(service.id),
      },
    ],
  })

  await alert.present()
}

// Handle delete
async function handleDelete(id: number) {
  const result = await servicesStore.deleteService(id)

  if (result.success) {
    const toast = await toastController.create({
      message: 'Услуга удалена',
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка удаления',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}

// Handle delete from modal
async function handleDeleteFromModal() {
  if (!selectedService.value) return

  const alert = await alertController.create({
    header: 'Удаление услуги',
    message: `Вы уверены, что хотите удалить "${selectedService.value.name}"?`,
    buttons: [
      {
        text: 'Отмена',
        role: 'cancel',
      },
      {
        text: 'Удалить',
        role: 'destructive',
        handler: async () => {
          await handleDelete(selectedService.value!.id)
          closeModal()
        },
      },
    ],
  })

  await alert.present()
}
</script>

<style scoped>
.content-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.add-service-button {
  --padding-start: 12px;
  --padding-end: 12px;
  margin: 0;
}

.back-to-home-container {
  padding: 24px 0;
}

/* Loading & Empty States */
.loading-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  padding: 24px;
  text-align: center;
}

.empty-state p {
  color: var(--ion-color-medium);
  margin: 0;
}

.empty-state ion-icon {
  font-size: 64px;
}

/* Service Card */
.service-card {
  width: 100%;
  padding: 12px 0;
}

/* Service Photo */
.service-photo {
  width: 100%;
  height: 200px;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.service-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.service-photo-placeholder {
  width: 100%;
  height: 200px;
  margin-bottom: 12px;
  border-radius: 8px;
  background: var(--ion-color-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--ion-color-medium);
}

.service-photo-placeholder ion-icon {
  font-size: 48px;
}

.service-photo-placeholder span {
  font-size: 0.9rem;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.service-info {
  flex: 1;
}

.service-info h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.service-toggle {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.service-description {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
  white-space: pre-line;
  line-height: 1.4;
}

.service-details {
  display: flex;
  gap: 16px;
  align-items: center;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-item ion-icon {
  font-size: 18px;
}

.detail-value {
  font-size: 0.95rem;
  font-weight: 500;
}
</style>
