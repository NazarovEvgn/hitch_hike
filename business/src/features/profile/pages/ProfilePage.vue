<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-menu-button></ion-menu-button>
        </ion-buttons>
        <ion-title>Профиль</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Loading -->
      <div v-if="profileStore.loading && !profileStore.business" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Form -->
      <div v-else-if="profileStore.business" class="profile-form ion-padding">
        <form @submit.prevent="handleSubmit">
          <!-- Business Name -->
          <div class="form-group">
            <label class="form-label">Название бизнеса</label>
            <ion-input
              v-model="formData.name"
              type="text"
              placeholder="Введите название"
              :class="{ 'ion-invalid': errors.name, 'ion-touched': true }"
              required
            ></ion-input>
            <div v-if="errors.name" class="error-text">{{ errors.name }}</div>
          </div>

          <!-- Business Type -->
          <div class="form-group">
            <label class="form-label">Тип бизнеса</label>
            <ion-select
              v-model="formData.business_type"
              placeholder="Выберите тип"
              interface="action-sheet"
              :class="{ 'ion-invalid': errors.business_type, 'ion-touched': true }"
            >
              <ion-select-option value="car_wash">Автомойка</ion-select-option>
              <ion-select-option value="auto_repair">Автосервис</ion-select-option>
              <ion-select-option value="tire_service">Шиномонтаж</ion-select-option>
              <ion-select-option value="beauty_salon">Салон красоты</ion-select-option>
            </ion-select>
            <div v-if="errors.business_type" class="error-text">{{ errors.business_type }}</div>
          </div>

          <!-- Address -->
          <div class="form-group">
            <label class="form-label">Адрес</label>
            <ion-input
              v-model="formData.address"
              type="text"
              placeholder="Введите адрес"
              :class="{ 'ion-invalid': errors.address, 'ion-touched': true }"
              required
            ></ion-input>
            <div v-if="errors.address" class="error-text">{{ errors.address }}</div>
          </div>

          <!-- Phone -->
          <div class="form-group">
            <label class="form-label">Телефон</label>
            <ion-input
              v-model="formData.phone"
              type="tel"
              placeholder="+7 (xxx) xxx-xx-xx"
              :class="{ 'ion-invalid': errors.phone, 'ion-touched': true }"
              required
            ></ion-input>
            <div v-if="errors.phone" class="error-text">{{ errors.phone }}</div>
          </div>

          <!-- Description -->
          <div class="form-group">
            <label class="form-label">Описание</label>
            <ion-textarea
              v-model="formData.description"
              rows="4"
              placeholder="Краткое описание вашего бизнеса"
              :class="{ 'ion-invalid': errors.description, 'ion-touched': true }"
            ></ion-textarea>
            <div v-if="errors.description" class="error-text">{{ errors.description }}</div>
          </div>

          <!-- Logo URL -->
          <div class="form-group">
            <label class="form-label">URL логотипа</label>
            <ion-input
              v-model="formData.logo_url"
              type="url"
              placeholder="https://example.com/logo.png"
              :class="{ 'ion-invalid': errors.logo_url, 'ion-touched': true }"
            ></ion-input>
            <div v-if="errors.logo_url" class="error-text">{{ errors.logo_url }}</div>
          </div>

          <!-- Coordinates (Read-only) -->
          <div class="form-group">
            <label class="form-label">Координаты (только для чтения)</label>
            <div class="coordinates-display">
              <div class="coordinate-item">
                <span class="coordinate-label">Широта:</span>
                <span class="coordinate-value">{{ profileStore.business.latitude }}</span>
              </div>
              <div class="coordinate-item">
                <span class="coordinate-label">Долгота:</span>
                <span class="coordinate-value">{{ profileStore.business.longitude }}</span>
              </div>
            </div>
          </div>

          <!-- Email (Read-only) -->
          <div class="form-group">
            <label class="form-label">Email (только для чтения)</label>
            <ion-input
              :value="profileStore.business.email"
              type="email"
              readonly
              disabled
            ></ion-input>
            <p class="help-text">Email нельзя изменить. Он используется для входа в систему.</p>
          </div>

          <!-- Submit Button -->
          <ion-button
            expand="block"
            type="submit"
            color="primary"
            :disabled="isSubmitting"
            class="submit-button"
          >
            <ion-spinner v-if="isSubmitting" name="crescent"></ion-spinner>
            <span v-else>Сохранить изменения</span>
          </ion-button>
        </form>
      </div>

      <!-- Error State -->
      <div v-else class="error-state">
        <ion-icon :icon="alertCircleOutline" size="large" color="danger"></ion-icon>
        <p>Не удалось загрузить профиль</p>
        <ion-button @click="profileStore.fetchProfile()" color="primary">
          Попробовать снова
        </ion-button>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonMenuButton,
  IonTitle,
  IonContent,
  IonInput,
  IonTextarea,
  IonSelect,
  IonSelectOption,
  IonButton,
  IonIcon,
  IonSpinner,
  toastController,
} from '@ionic/vue'
import { alertCircleOutline } from 'ionicons/icons'
import { useProfileStore } from '../stores/profileStore'
import type { BusinessUpdateInput } from '../types'

const profileStore = useProfileStore()

const formData = reactive<BusinessUpdateInput>({
  name: '',
  business_type: 'car_wash',
  address: '',
  phone: '',
  description: '',
  logo_url: '',
})

const errors = reactive<Partial<Record<keyof BusinessUpdateInput, string>>>({})
const isSubmitting = ref(false)

onMounted(async () => {
  await profileStore.fetchProfile()

  // Populate form with current data
  if (profileStore.business) {
    formData.name = profileStore.business.name
    formData.business_type = profileStore.business.business_type
    formData.address = profileStore.business.address
    formData.phone = profileStore.business.phone
    formData.description = profileStore.business.description || ''
    formData.logo_url = profileStore.business.logo_url || ''
  }
})

function validateForm(): boolean {
  Object.keys(errors).forEach(key => delete errors[key as keyof BusinessUpdateInput])

  if (!formData.name.trim()) {
    errors.name = 'Название обязательно'
  }

  if (!formData.address.trim()) {
    errors.address = 'Адрес обязателен'
  }

  if (!formData.phone.trim()) {
    errors.phone = 'Телефон обязателен'
  }

  return Object.keys(errors).length === 0
}

async function handleSubmit() {
  if (!validateForm()) {
    const toast = await toastController.create({
      message: 'Пожалуйста, исправьте ошибки в форме',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
    return
  }

  isSubmitting.value = true

  const result = await profileStore.updateProfile(formData)

  isSubmitting.value = false

  if (result.success) {
    const toast = await toastController.create({
      message: 'Профиль успешно обновлен',
      duration: 2000,
      color: 'success',
      position: 'top',
    })
    await toast.present()
  } else {
    const toast = await toastController.create({
      message: result.error || 'Ошибка при сохранении',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}
</script>

<style scoped>
.loading-container,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  padding: 24px;
}

.error-state p {
  color: var(--ion-color-medium);
  margin: 0;
}

.error-state ion-icon {
  font-size: 64px;
}

.profile-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 16px;
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

.error-text {
  color: var(--ion-color-danger);
  font-size: 0.85rem;
  margin-top: 4px;
}

.help-text {
  font-size: 0.85rem;
  color: var(--ion-color-medium);
  margin: 8px 0 0 0;
}

.coordinates-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--ion-color-light);
  border-radius: 8px;
}

.coordinate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coordinate-label {
  font-weight: 500;
  color: var(--ion-color-medium);
}

.coordinate-value {
  font-weight: 600;
  color: var(--ion-color-dark);
}

.submit-button {
  margin-top: 32px;
}

ion-input,
ion-textarea,
ion-select {
  --background: var(--ion-color-light);
  --padding-start: 12px;
  --padding-end: 12px;
  border-radius: 8px;
}

ion-input.ion-invalid,
ion-textarea.ion-invalid,
ion-select.ion-invalid {
  --border-color: var(--ion-color-danger);
}
</style>
