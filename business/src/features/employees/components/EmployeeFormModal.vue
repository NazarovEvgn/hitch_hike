<template>
  <ion-modal :is-open="isOpen" @didDismiss="handleClose">
    <ion-header>
      <ion-toolbar>
        <ion-title>{{ employee ? 'Редактировать мастера' : 'Добавить мастера' }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleClose">Закрыть</ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <form @submit.prevent="handleSubmit" class="employee-form">
        <!-- Photo Upload -->
        <div class="form-group">
          <label class="form-label">Фото мастера</label>
          <PhotoUpload
            v-model="formData.photo_url"
            label="Добавить фото мастера"
          />
        </div>

        <!-- Name -->
        <div class="form-group">
          <label class="form-label">ФИО *</label>
          <ion-input
            v-model="formData.name"
            type="text"
            placeholder="Введите ФИО"
            required
          ></ion-input>
        </div>

        <!-- Phone -->
        <div class="form-group">
          <label class="form-label">Телефон *</label>
          <ion-input
            v-model="formData.phone"
            type="tel"
            placeholder="+7 (xxx) xxx-xx-xx"
            required
          ></ion-input>
        </div>

        <!-- Services Selection -->
        <div class="form-group">
          <label class="form-label">Услуги, которые выполняет мастер</label>
          <ion-accordion-group>
            <ion-accordion value="services">
              <ion-item slot="header" color="light">
                <ion-label>
                  {{ selectedServicesText }}
                </ion-label>
              </ion-item>
              <div slot="content" class="services-list">
                <ion-item
                  v-for="service in availableServices"
                  :key="service.id"
                  lines="none"
                >
                  <ion-checkbox
                    slot="start"
                    :checked="formData.service_ids.includes(service.id)"
                    @ionChange="toggleService(service.id)"
                  ></ion-checkbox>
                  <ion-label>{{ service.name }}</ion-label>
                </ion-item>

                <div v-if="availableServices.length === 0" class="empty-services">
                  <p>Нет доступных услуг. Сначала добавьте услуги в разделе "Услуги и цены".</p>
                </div>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </div>

        <!-- Active Status Toggle (only for editing) -->
        <div v-if="employee" class="form-group">
          <ion-item lines="none">
            <ion-toggle v-model="formData.is_active" color="success">
              <span slot="label">{{ formData.is_active ? 'Активен' : 'Неактивен' }}</span>
            </ion-toggle>
          </ion-item>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <ion-button
            expand="block"
            color="primary"
            type="submit"
            :disabled="isSaving || !isFormValid"
          >
            <ion-spinner v-if="isSaving" name="crescent"></ion-spinner>
            <span v-else>{{ employee ? 'Сохранить' : 'Добавить' }}</span>
          </ion-button>

          <ion-button
            v-if="employee"
            expand="block"
            color="danger"
            fill="outline"
            @click="handleDelete"
            :disabled="isSaving"
          >
            Удалить
          </ion-button>
        </div>
      </form>
    </ion-content>
  </ion-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonInput,
  IonToggle,
  IonItem,
  IonLabel,
  IonCheckbox,
  IonAccordion,
  IonAccordionGroup,
  IonSpinner,
} from '@ionic/vue'
import PhotoUpload from '@/shared/components/PhotoUpload.vue'
import type { Employee, EmployeeFormData } from '../types'
import type { Service } from '@/features/services/types'

interface Props {
  isOpen: boolean
  employee: Employee | null
  availableServices: Service[]
}

interface Emits {
  (e: 'close'): void
  (e: 'save', data: EmployeeFormData): void
  (e: 'delete'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isSaving = ref(false)

const formData = reactive<EmployeeFormData>({
  name: '',
  phone: '',
  photo_url: null,
  is_active: true,
  service_ids: [],
})

const isFormValid = computed(() => {
  return formData.name.trim() !== '' && formData.phone.trim() !== ''
})

const selectedServicesText = computed(() => {
  const count = formData.service_ids.length
  if (count === 0) return 'Выберите услуги'
  if (count === 1) return '1 услуга выбрана'
  if (count < 5) return `${count} услуги выбраны`
  return `${count} услуг выбрано`
})

// Watch for employee changes to populate form
watch(
  () => props.employee,
  (newEmployee) => {
    if (newEmployee) {
      formData.name = newEmployee.name
      formData.phone = newEmployee.phone
      formData.photo_url = newEmployee.photo_url
      formData.is_active = newEmployee.is_active
      formData.service_ids = [...newEmployee.service_ids]
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.name = ''
  formData.phone = ''
  formData.photo_url = null
  formData.is_active = true
  formData.service_ids = []
}

function toggleService(serviceId: number) {
  const index = formData.service_ids.indexOf(serviceId)
  if (index > -1) {
    formData.service_ids.splice(index, 1)
  } else {
    formData.service_ids.push(serviceId)
  }
}

function handleClose() {
  resetForm()
  emit('close')
}

async function handleSubmit() {
  if (!isFormValid.value) return

  isSaving.value = true
  emit('save', { ...formData })
  isSaving.value = false
}

function handleDelete() {
  emit('delete')
}
</script>

<style scoped>
.employee-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--ion-color-dark);
}

ion-input,
ion-textarea {
  --background: var(--ion-color-light);
  --padding-start: 12px;
  --padding-end: 12px;
  border-radius: 8px;
}

.services-list {
  padding: 8px 0;
}

.services-list ion-item {
  --padding-start: 16px;
  --padding-end: 16px;
  margin: 4px 0;
}

.empty-services {
  padding: 16px;
  text-align: center;
}

.empty-services p {
  color: var(--ion-color-medium);
  margin: 0;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 32px;
}
</style>
