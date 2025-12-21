<template>
  <ion-page>
    <AppHeader />

    <ion-content :fullscreen="true">
      <PageNavigation page-title="Профиль" />

      <!-- Loading -->
      <div v-if="profileStore.loading && !profileStore.business" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Form -->
      <div v-else-if="profileStore.business" class="profile-form ion-padding">
        <form @submit.prevent="handleSubmit">
          <!-- Logo Photo -->
          <div class="form-group">
            <label class="form-label">Логотип</label>
            <PhotoUpload
              v-model="formData.logo_url"
              label="Добавить логотип"
            />
          </div>

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

          <!-- Phones -->
          <div class="form-group">
            <div class="phones-header">
              <label class="form-label">Телефоны</label>
              <ion-button fill="clear" size="small" @click="addPhone">
                <ion-icon slot="start" :icon="addOutline"></ion-icon>
                Добавить
              </ion-button>
            </div>
            <div v-for="(phone, index) in formData.phones" :key="index" class="phone-input-row">
              <ion-input
                v-model="formData.phones[index]"
                type="tel"
                :placeholder="`Телефон ${index + 1}`"
                :class="{ 'ion-invalid': errors.phones?.[index], 'ion-touched': true }"
                required
              ></ion-input>
              <ion-button
                v-if="formData.phones.length > 1"
                fill="clear"
                color="danger"
                @click="removePhone(index)"
              >
                <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
              </ion-button>
            </div>
            <div v-if="errors.phones" class="error-text">{{ errors.phones }}</div>
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

          <!-- Business Hours Accordion -->
          <div class="hours-accordion-container">
            <ion-accordion-group>
              <ion-accordion value="business-hours">
                <ion-item slot="header" color="light">
                  <ion-label>
                    <h3>Часы работы</h3>
                  </ion-label>
                </ion-item>
                <div class="ion-padding" slot="content">
                  <BusinessHoursForm />
                </div>
              </ion-accordion>
            </ion-accordion-group>
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

      <!-- Back to Home Button -->
      <div class="back-to-home-container">
        <ion-button expand="block" fill="outline" color="medium" @click="$router.push('/dashboard')">
          <ion-icon slot="start" :icon="homeOutline"></ion-icon>
          На главную
        </ion-button>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  IonPage,
  IonContent,
  IonInput,
  IonTextarea,
  IonSelect,
  IonSelectOption,
  IonButton,
  IonIcon,
  IonSpinner,
  IonAccordion,
  IonAccordionGroup,
  IonItem,
  IonLabel,
  toastController,
} from '@ionic/vue'
import { alertCircleOutline, homeOutline, addOutline, trashOutline } from 'ionicons/icons'
import { useProfileStore } from '../stores/profileStore'
import type { BusinessUpdateInput } from '../types'
import AppHeader from '@/shared/components/AppHeader.vue'
import PageNavigation from '@/shared/components/PageNavigation.vue'
import BusinessHoursForm from '@/features/business-hours/components/BusinessHoursForm.vue'
import PhotoUpload from '@/shared/components/PhotoUpload.vue'

const profileStore = useProfileStore()

const formData = reactive<BusinessUpdateInput>({
  name: '',
  business_type: 'car_wash',
  address: '',
  phones: [''],
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
    formData.phones = profileStore.business.phones.length > 0 ? [...profileStore.business.phones] : ['']
    formData.description = profileStore.business.description || ''
    formData.logo_url = profileStore.business.logo_url || ''
  }
})

function addPhone() {
  formData.phones.push('')
}

function removePhone(index: number) {
  if (formData.phones.length > 1) {
    formData.phones.splice(index, 1)
  }
}

function validateForm(): boolean {
  Object.keys(errors).forEach(key => delete errors[key as keyof BusinessUpdateInput])

  if (!formData.name.trim()) {
    errors.name = 'Название обязательно'
  }

  if (!formData.address.trim()) {
    errors.address = 'Адрес обязателен'
  }

  // Validate phones
  if (formData.phones.length === 0 || formData.phones.every(p => !p.trim())) {
    errors.phones = 'Укажите хотя бы один телефон'
  } else {
    // Filter out empty phones
    formData.phones = formData.phones.filter(p => p.trim())
    if (formData.phones.length === 0) {
      formData.phones = ['']
      errors.phones = 'Укажите хотя бы один телефон'
    }
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

.phones-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.phones-header ion-button {
  margin: 0;
  --padding-start: 8px;
  --padding-end: 8px;
}

.phone-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.phone-input-row ion-input {
  flex: 1;
}

.phone-input-row ion-button {
  --padding-start: 8px;
  --padding-end: 8px;
  margin: 0;
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

.back-to-home-container {
  padding: 24px 16px;
  max-width: 600px;
  margin: 0 auto;
}

.submit-button {
  margin-top: 32px;
}

.hours-accordion-container {
  margin-top: 32px;
  margin-bottom: 24px;
}

.hours-accordion-container ion-accordion-group {
  border: 2px solid var(--ion-color-medium-tint);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.hours-accordion-container ion-accordion-group:hover {
  border-color: var(--ion-color-primary);
  box-shadow: 0 4px 12px rgba(39, 18, 106, 0.15);
}

.hours-accordion-container ion-item {
  --border-radius: 0;
  cursor: pointer;
}

.hours-accordion-container ion-label h3 {
  margin: 0;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--ion-color-dark);
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
