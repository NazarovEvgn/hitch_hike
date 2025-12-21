<template>
  <ion-page>
    <AppHeader />

    <ion-content :fullscreen="true">
      <PageNavigation page-title="Мастера" />

      <div class="content-container">
        <!-- Loading State -->
        <div v-if="employeesStore.loading && employeesStore.employees.length === 0" class="loading-container">
          <ion-spinner name="crescent"></ion-spinner>
        </div>

        <!-- Empty State -->
        <div v-else-if="!employeesStore.loading && employeesStore.employees.length === 0" class="empty-state">
          <ion-icon :icon="peopleOutline" size="large" color="medium"></ion-icon>
          <p>Нет добавленных мастеров</p>
          <ion-button @click="openCreateModal">Добавить первого мастера</ion-button>
        </div>

        <!-- Employees Section -->
        <div v-else>
          <!-- Section Header -->
          <div class="section-header">
            <ion-button fill="clear" @click="openCreateModal" class="add-button">
              <ion-icon slot="start" :icon="addOutline"></ion-icon>
              Добавить
            </ion-button>
          </div>

          <!-- Employees List -->
          <ion-list>
            <ion-item-sliding v-for="employee in employeesStore.employees" :key="employee.id">
              <ion-item button @click="openEditModal(employee)">
                <div class="employee-card">
                  <!-- Employee Photo -->
                  <div v-if="employee.photo_url" class="employee-photo">
                    <img :src="getPhotoUrl(employee.photo_url)" :alt="employee.name" />
                  </div>
                  <div v-else class="employee-photo-placeholder">
                    <ion-icon :icon="personOutline" size="large"></ion-icon>
                  </div>

                  <!-- Employee Header -->
                  <div class="employee-header">
                    <div class="employee-info">
                      <h3>{{ employee.name }}</h3>
                      <p class="phone">{{ employee.phone }}</p>
                    </div>
                    <div class="employee-toggle" @click.stop>
                      <ion-toggle
                        :checked="employee.is_active"
                        @ion-change="toggleActive(employee.id)"
                        color="success"
                      ></ion-toggle>
                    </div>
                  </div>

                  <!-- Employee Services -->
                  <div v-if="employee.service_ids.length > 0" class="employee-services">
                    <div class="services-label">Услуги:</div>
                    <div class="services-tags">
                      <ion-badge
                        v-for="serviceId in employee.service_ids"
                        :key="serviceId"
                        color="primary"
                      >
                        {{ getServiceName(serviceId) }}
                      </ion-badge>
                    </div>
                  </div>

                  <!-- Status Badge -->
                  <div class="employee-status">
                    <ion-badge :color="employee.is_active ? 'success' : 'medium'">
                      {{ employee.is_active ? 'Активен' : 'Неактивен' }}
                    </ion-badge>
                  </div>
                </div>
              </ion-item>

              <ion-item-options>
                <ion-item-option color="primary" @click="openEditModal(employee)">
                  <ion-icon slot="icon-only" :icon="createOutline"></ion-icon>
                </ion-item-option>
                <ion-item-option color="danger" @click="confirmDelete(employee)">
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

    <!-- Employee Form Modal -->
    <EmployeeFormModal
      :is-open="isModalOpen"
      :employee="selectedEmployee"
      :available-services="servicesStore.services"
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
  peopleOutline,
  personOutline,
  createOutline,
  trashOutline,
  homeOutline,
} from 'ionicons/icons'
import { useEmployeesStore } from '../stores/employeesStore'
import { useServicesStore } from '@/features/services/stores/servicesStore'
import EmployeeFormModal from '../components/EmployeeFormModal.vue'
import type { Employee, EmployeeFormData } from '../types'
import AppHeader from '@/shared/components/AppHeader.vue'
import PageNavigation from '@/shared/components/PageNavigation.vue'

const employeesStore = useEmployeesStore()
const servicesStore = useServicesStore()
const isModalOpen = ref(false)
const selectedEmployee = ref<Employee | null>(null)

// Load employees and services on mount
onMounted(async () => {
  await Promise.all([
    employeesStore.fetchEmployees(),
    servicesStore.fetchServices(),
  ])
})

// Get full photo URL
function getPhotoUrl(photoUrl: string | null): string {
  if (!photoUrl) return ''
  if (photoUrl.startsWith('http')) return photoUrl
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  return `${apiUrl}${photoUrl}`
}

// Get service name by ID
function getServiceName(serviceId: number): string {
  const service = servicesStore.services.find(s => s.id === serviceId)
  return service?.name || 'Неизвестная услуга'
}

// Open create modal
function openCreateModal() {
  selectedEmployee.value = null
  isModalOpen.value = true
}

// Open edit modal
function openEditModal(employee: Employee) {
  selectedEmployee.value = employee
  isModalOpen.value = true
}

// Close modal
function closeModal() {
  isModalOpen.value = false
  selectedEmployee.value = null
}

// Handle save (create or update)
async function handleSave(formData: EmployeeFormData) {
  let result

  if (selectedEmployee.value) {
    // Update existing employee
    result = await employeesStore.updateEmployee(selectedEmployee.value.id, formData)
  } else {
    // Create new employee
    result = await employeesStore.createEmployee(formData)
  }

  if (result.success) {
    const toast = await toastController.create({
      message: selectedEmployee.value ? 'Мастер обновлен' : 'Мастер добавлен',
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

// Toggle employee active status
async function toggleActive(id: number) {
  const result = await employeesStore.toggleEmployeeActive(id)

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
async function confirmDelete(employee: Employee) {
  const alert = await alertController.create({
    header: 'Удаление мастера',
    message: `Вы уверены, что хотите удалить "${employee.name}"?`,
    buttons: [
      {
        text: 'Отмена',
        role: 'cancel',
      },
      {
        text: 'Удалить',
        role: 'destructive',
        handler: () => handleDelete(employee.id),
      },
    ],
  })

  await alert.present()
}

// Handle delete
async function handleDelete(id: number) {
  const result = await employeesStore.deleteEmployee(id)

  if (result.success) {
    const toast = await toastController.create({
      message: 'Мастер удален',
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
  if (!selectedEmployee.value) return

  const alert = await alertController.create({
    header: 'Удаление мастера',
    message: `Вы уверены, что хотите удалить "${selectedEmployee.value.name}"?`,
    buttons: [
      {
        text: 'Отмена',
        role: 'cancel',
      },
      {
        text: 'Удалить',
        role: 'destructive',
        handler: async () => {
          await handleDelete(selectedEmployee.value!.id)
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
  justify-content: flex-end;
  align-items: center;
  margin: 16px 0;
}

.add-button {
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

/* Employee Card */
.employee-card {
  width: 100%;
  padding: 12px 0;
}

/* Employee Photo */
.employee-photo {
  width: 80px;
  height: 80px;
  margin-bottom: 12px;
  border-radius: 50%;
  overflow: hidden;
}

.employee-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.employee-photo-placeholder {
  width: 80px;
  height: 80px;
  margin-bottom: 12px;
  border-radius: 50%;
  background: var(--ion-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ion-color-medium);
}

.employee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.employee-info {
  flex: 1;
}

.employee-info h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}

.employee-info .phone {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
}

.employee-toggle {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.employee-services {
  margin-bottom: 12px;
}

.services-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--ion-color-medium);
  margin-bottom: 6px;
}

.services-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.services-tags ion-badge {
  font-size: 0.75rem;
  padding: 4px 8px;
}

.employee-status {
  display: flex;
  gap: 8px;
}
</style>
