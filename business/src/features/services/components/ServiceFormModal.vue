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
            :rows="6"
            :auto-grow="true"
          ></ion-textarea>
        </ion-item>

        <!-- Photo Upload -->
        <div class="form-item photo-upload-container">
          <label class="photo-label">Фотография услуги</label>
          <PhotoUpload v-model="formData.photo_url" label="Добавить фото услуги" />
        </div>

        <!-- Price Fields - Range (default) -->
        <div v-if="!isFixedPrice" class="row">
          <ion-item lines="none" class="form-item col">
            <ion-label position="stacked">Цена от (₽) *</ion-label>
            <ion-input
              v-model.number="formData.price_from"
              type="number"
              min="0"
              step="10"
              placeholder="0"
              required
            ></ion-input>
          </ion-item>

          <ion-item lines="none" class="form-item col">
            <ion-label position="stacked">Цена до (₽) *</ion-label>
            <ion-input
              v-model.number="formData.price_to"
              type="number"
              min="0"
              step="10"
              placeholder="0"
              required
            ></ion-input>
          </ion-item>
        </div>

        <!-- Price Field - Fixed -->
        <div v-else class="price-container">
          <ion-item lines="none" class="form-item">
            <ion-label position="stacked">Цена (₽) *</ion-label>
            <ion-input
              v-model.number="formData.price_from"
              type="number"
              min="0"
              step="10"
              placeholder="0"
              required
            ></ion-input>
          </ion-item>
        </div>

        <!-- Price Type Checkbox -->
        <ion-item lines="none" class="form-item checkbox-item">
          <ion-checkbox v-model="isFixedPrice" @ionChange="handlePriceTypeChange">
            Указать фиксированную цену
          </ion-checkbox>
        </ion-item>

        <!-- Duration -->
        <ion-item lines="none" class="form-item">
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

        <!-- Active Toggle -->
        <ion-item lines="none" class="form-item toggle-item">
          <ion-label>Услуга активна</ion-label>
          <ion-toggle v-model="formData.is_active" color="success" slot="end"></ion-toggle>
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
  IonCheckbox,
} from '@ionic/vue'
import { closeOutline, trashOutline } from 'ionicons/icons'
import type { Service, ServiceFormData } from '../types'
import PhotoUpload from '@/shared/components/PhotoUpload.vue'

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
  price_from: 0,
  price_to: 0,
  duration_minutes: 30,
  photo_url: null,
  is_active: true,
})

// Price type state
const isFixedPrice = ref(false)

// Computed
const isEditMode = computed(() => props.service !== null)

const isFormValid = computed(() => {
  const baseValid =
    formData.value.name.trim() !== '' &&
    formData.value.price_from >= 0 &&
    formData.value.duration_minutes > 0

  if (isFixedPrice.value) {
    return baseValid
  }

  return baseValid && formData.value.price_to >= 0 && formData.value.price_to >= formData.value.price_from
})

// Watch service prop to populate form
watch(
  () => props.service,
  (newService) => {
    if (newService) {
      formData.value = {
        name: newService.name,
        description: newService.description || '',
        price_from: newService.price_from,
        price_to: newService.price_to,
        duration_minutes: newService.duration_minutes,
        photo_url: newService.photo_url || null,
        is_active: newService.is_active,
      }
      // Always start with range fields (checkbox unchecked)
      isFixedPrice.value = false
    } else {
      // Reset form for create mode
      formData.value = {
        name: '',
        description: '',
        price_from: 0,
        price_to: 0,
        duration_minutes: 30,
        photo_url: null,
        is_active: true,
      }
      isFixedPrice.value = false
    }
  },
  { immediate: true }
)

// Handlers
function handleClose() {
  emit('close')
}

function handlePriceTypeChange() {
  if (isFixedPrice.value) {
    // When switching to fixed price, set price_to to price_from
    formData.value.price_to = formData.value.price_from
  }
}

function handleSubmit() {
  if (!isFormValid.value) return

  const submitData = { ...formData.value }

  // If fixed price, ensure price_to equals price_from
  if (isFixedPrice.value) {
    submitData.price_to = submitData.price_from
  }

  emit('save', submitData)
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

/* Checkbox Item */
.checkbox-item {
  --background: transparent;
  --padding-start: 0;
  --padding-end: 0;
  --inner-padding-end: 0;
  margin-bottom: 16px;
}

.checkbox-item ion-checkbox {
  margin-right: 12px;
}

/* Toggle Item */
.toggle-item ion-label {
  margin-right: auto;
}

/* Photo Upload Container */
.photo-upload-container {
  margin-bottom: 16px;
}

.photo-label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 0.875rem;
  color: var(--ion-color-dark);
}

/* Price Container */
.price-container {
  margin-bottom: 0;
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
