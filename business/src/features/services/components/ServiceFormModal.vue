<template>
  <ion-modal :is-open="isOpen" @did-dismiss="handleClose">
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>{{ isEditMode ? 'Редактировать услугу' : 'Новая услуга' }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleClose">
            <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <form @submit.prevent="handleSubmit">
        <!-- Name -->
        <ion-item lines="none" class="form-item">
          <ion-label position="stacked">Название услуги *</ion-label>
          <ion-input
            v-model="formData.name"
            type="text"
            placeholder="Например: Мойка кузова"
            required
          ></ion-input>
        </ion-item>

        <!-- Description -->
        <ion-item lines="none" class="form-item">
          <ion-label position="stacked">Описание</ion-label>
          <ion-textarea
            v-model="formData.description"
            placeholder="Краткое описание услуги"
            :rows="3"
          ></ion-textarea>
        </ion-item>

        <!-- Price & Duration Row -->
        <div class="row">
          <ion-item lines="none" class="form-item col">
            <ion-label position="stacked">Цена (₽) *</ion-label>
            <ion-input
              v-model.number="formData.price"
              type="number"
              min="0"
              step="10"
              placeholder="0"
              required
            ></ion-input>
          </ion-item>

          <ion-item lines="none" class="form-item col">
            <ion-label position="stacked">Длительность (мин) *</ion-label>
            <ion-input
              v-model.number="formData.duration_minutes"
              type="number"
              min="5"
              step="5"
              placeholder="30"
              required
            ></ion-input>
          </ion-item>
        </div>

        <!-- Active Toggle -->
        <ion-item lines="none" class="form-item">
          <ion-label>Услуга активна</ion-label>
          <ion-toggle v-model="formData.is_active" color="success"></ion-toggle>
        </ion-item>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <ion-button expand="block" color="medium" fill="outline" @click="handleClose">
            Отмена
          </ion-button>
          <ion-button expand="block" type="submit" :disabled="!isFormValid">
            Сохранить
          </ion-button>
        </div>

        <!-- Delete Button (Only in Edit Mode) -->
        <div v-if="isEditMode" class="delete-button-container">
          <ion-button expand="block" color="danger" fill="outline" @click="handleDelete">
            <ion-icon slot="start" :icon="trashOutline"></ion-icon>
            Удалить услугу
          </ion-button>
        </div>
      </form>
    </ion-content>
  </ion-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonItem,
  IonLabel,
  IonInput,
  IonTextarea,
  IonToggle,
  IonIcon,
} from '@ionic/vue'
import { closeOutline, trashOutline } from 'ionicons/icons'
import type { Service, ServiceFormData } from '../types'

interface Props {
  isOpen: boolean
  service: Service | null
}

interface Emits {
  (e: 'close'): void
  (e: 'save', formData: ServiceFormData): void
  (e: 'delete'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Form data
const formData = ref<ServiceFormData>({
  name: '',
  description: '',
  price: 0,
  duration_minutes: 30,
  is_active: true,
})

// Computed
const isEditMode = computed(() => props.service !== null)

const isFormValid = computed(() => {
  return (
    formData.value.name.trim() !== '' &&
    formData.value.price >= 0 &&
    formData.value.duration_minutes > 0
  )
})

// Watch service prop to populate form
watch(
  () => props.service,
  (newService) => {
    if (newService) {
      formData.value = {
        name: newService.name,
        description: newService.description || '',
        price: newService.price,
        duration_minutes: newService.duration_minutes,
        is_active: newService.is_active,
      }
    } else {
      // Reset form for create mode
      formData.value = {
        name: '',
        description: '',
        price: 0,
        duration_minutes: 30,
        is_active: true,
      }
    }
  },
  { immediate: true }
)

// Handlers
function handleClose() {
  emit('close')
}

function handleSubmit() {
  if (!isFormValid.value) return

  emit('save', {
    ...formData.value,
  })
}

function handleDelete() {
  emit('delete')
}
</script>

<style scoped>
.form-item {
  --background: var(--ion-color-light);
  --border-radius: 8px;
  --padding-start: 16px;
  --padding-end: 16px;
  margin-bottom: 16px;
}

ion-label[position='stacked'] {
  font-weight: 500;
  margin-bottom: 8px;
}

/* Two Column Row */
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.col {
  margin-bottom: 16px;
}

/* Action Buttons */
.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 24px;
}

/* Delete Button */
.delete-button-container {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--ion-color-light-shade);
}
</style>
