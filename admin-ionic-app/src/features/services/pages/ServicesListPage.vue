<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-menu-button></ion-menu-button>
        </ion-buttons>
        <ion-title>Услуги</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="openCreateModal">
            <ion-icon slot="icon-only" :icon="addOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
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

      <!-- Services List -->
      <ion-list v-else>
        <ion-item-sliding v-for="service in servicesStore.services" :key="service.id">
          <ion-item>
            <div class="service-card">
              <!-- Service Header -->
              <div class="service-header">
                <div class="service-info">
                  <h3>{{ service.name }}</h3>
                  <p v-if="service.description" class="service-description">
                    {{ service.description }}
                  </p>
                </div>
                <ion-toggle
                  :checked="service.is_active"
                  @ion-change="toggleActive(service.id)"
                  color="success"
                ></ion-toggle>
              </div>

              <!-- Service Details -->
              <div class="service-details">
                <div class="detail-item">
                  <ion-icon :icon="cashOutline" color="primary"></ion-icon>
                  <span class="detail-value">{{ formatPrice(service.price) }}</span>
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
    </ion-content>

    <!-- Service Form Modal -->
    <ServiceFormModal
      :is-open="isModalOpen"
      :service="selectedService"
      @close="closeModal"
      @save="handleSave"
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
  IonList,
  IonItem,
  IonItemSliding,
  IonItemOptions,
  IonItemOption,
  IonIcon,
  IonToggle,
  IonBadge,
  IonSpinner,
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
} from 'ionicons/icons'
import { useServicesStore } from '../stores/servicesStore'
import ServiceFormModal from '../components/ServiceFormModal.vue'
import type { Service, ServiceFormData } from '../types'

const servicesStore = useServicesStore()
const isModalOpen = ref(false)
const selectedService = ref<Service | null>(null)

// Load services on mount
onMounted(async () => {
  await servicesStore.fetchServices()
})

// Format price to RUB
function formatPrice(price: number): string {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
  }).format(price)
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
</script>

<style scoped>
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

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.service-info {
  flex: 1;
}

.service-info h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.service-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
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
