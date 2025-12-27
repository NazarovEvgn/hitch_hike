<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-button @click="router.back()">
            <ion-icon slot="icon-only" :icon="arrowBackOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
        <ion-title>Настройки профиля</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Loading -->
      <div v-if="profileStore.loading && !profileStore.profile" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Profile Content -->
      <div v-else-if="profileStore.profile" class="profile-content">
        <!-- Profile Card - Avatar, Name, Phone -->
        <div class="profile-card">
          <!-- Avatar -->
          <div class="avatar-section">
            <div class="avatar-wrapper" @click="triggerFileInput">
              <img
                v-if="avatarPreview || profileStore.profile.avatar_url"
                :src="avatarPreview || getFullAvatarUrl(profileStore.profile.avatar_url)"
                alt="Avatar"
                class="avatar-image"
              />
              <div v-else class="avatar-placeholder">
                <ion-icon :icon="personOutline" size="large"></ion-icon>
              </div>
              <div class="avatar-overlay">
                <ion-icon :icon="cameraOutline"></ion-icon>
              </div>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleFileSelect"
            />
          </div>

          <!-- Name Display -->
          <div class="profile-name-display">
            {{ profileStore.profile.name }}
          </div>

          <!-- Phone Display -->
          <div class="profile-phone-display">
            {{ profileStore.profile.phone || 'Телефон не указан' }}
          </div>

          <!-- Delete Avatar Button -->
          <ion-button
            v-if="profileStore.profile.avatar_url"
            fill="clear"
            size="small"
            color="danger"
            @click="handleDeleteAvatar"
            class="delete-avatar-btn"
          >
            Удалить фото
          </ion-button>
        </div>

        <!-- Edit Form Section -->
        <div class="edit-section">
          <div class="section-title">Редактирование профиля</div>

          <ion-list class="edit-form">
            <ion-item>
              <ion-label position="floating">Ваше имя *</ion-label>
              <ion-input v-model="formData.name" type="text" required></ion-input>
            </ion-item>

            <ion-item>
              <ion-label position="floating">Пол</ion-label>
              <ion-select v-model="formData.gender" placeholder="Выберите" interface="action-sheet">
                <ion-select-option value="male">Мужской</ion-select-option>
                <ion-select-option value="female">Женский</ion-select-option>
                <ion-select-option value="other">Другой</ion-select-option>
              </ion-select>
            </ion-item>

            <ion-item>
              <ion-label position="floating">Телефон</ion-label>
              <ion-input :value="profileStore.profile.phone" type="tel" disabled></ion-input>
              <ion-note slot="helper">Используется для входа в приложение</ion-note>
            </ion-item>

            <ion-item>
              <ion-label position="floating">Почта</ion-label>
              <ion-input v-model="formData.email" type="email"></ion-input>
            </ion-item>
          </ion-list>

          <!-- Error Message -->
          <ion-text v-if="profileStore.error" color="danger" class="error-message">
            <p>{{ profileStore.error }}</p>
          </ion-text>

          <!-- Save Button -->
          <div class="button-section">
            <ion-button
              expand="block"
              :disabled="profileStore.loading || !isFormValid"
              @click="handleSave"
              size="large"
            >
              <ion-spinner v-if="profileStore.loading" name="crescent" />
              <span v-else>Сохранить изменения</span>
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonContent,
  IonList,
  IonItem,
  IonLabel,
  IonInput,
  IonSelect,
  IonSelectOption,
  IonIcon,
  IonSpinner,
  IonText,
  IonNote,
  toastController,
} from '@ionic/vue'
import {
  arrowBackOutline,
  personOutline,
  cameraOutline,
} from 'ionicons/icons'
import { useProfileStore } from '../stores/profileStore'
import type { Gender } from '../types'
import { API_BASE_URL } from '@/core/config'

const router = useRouter()
const profileStore = useProfileStore()

const formData = ref({
  name: '',
  gender: null as Gender | null,
  email: '',
})

const fileInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)
const selectedFile = ref<File | null>(null)

const isFormValid = computed(() => {
  return formData.value.name.trim().length > 0
})

onMounted(async () => {
  await profileStore.fetchProfile()
  if (profileStore.profile) {
    formData.value.name = profileStore.profile.name
    formData.value.gender = profileStore.profile.gender
    formData.value.email = profileStore.profile.email || ''
  }
})

function getFullAvatarUrl(avatarUrl: string | null): string {
  if (!avatarUrl) return ''
  // Remove /api/v1 from base URL and append avatar URL
  const baseUrl = API_BASE_URL.replace('/api/v1', '')
  return `${baseUrl}${avatarUrl}`
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast('Размер файла не должен превышать 5 МБ', 'danger')
      return
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      showToast('Пожалуйста, выберите изображение', 'danger')
      return
    }

    selectedFile.value = file

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)

    // Upload immediately
    handleUploadAvatar()
  }
}

async function handleUploadAvatar() {
  if (!selectedFile.value) return

  const success = await profileStore.uploadAvatar(selectedFile.value)
  if (success) {
    showToast('Фото профиля обновлено', 'success')
    avatarPreview.value = null
    selectedFile.value = null
  } else {
    showToast(profileStore.error || 'Не удалось загрузить фото', 'danger')
    avatarPreview.value = null
    selectedFile.value = null
  }
}

async function handleDeleteAvatar() {
  const success = await profileStore.deleteAvatar()
  if (success) {
    showToast('Фото профиля удалено', 'success')
  } else {
    showToast(profileStore.error || 'Не удалось удалить фото', 'danger')
  }
}

async function handleSave() {
  const updateData: any = {}

  // Only include changed fields
  if (formData.value.name !== profileStore.profile?.name) {
    updateData.name = formData.value.name
  }
  if (formData.value.gender !== profileStore.profile?.gender) {
    updateData.gender = formData.value.gender
  }
  if (formData.value.email !== (profileStore.profile?.email || '')) {
    updateData.email = formData.value.email || null
  }

  // If nothing changed, just show message
  if (Object.keys(updateData).length === 0) {
    showToast('Нет изменений для сохранения', 'warning')
    return
  }

  const success = await profileStore.updateProfile(updateData)
  if (success) {
    showToast('Профиль успешно обновлен', 'success')
  } else {
    showToast(profileStore.error || 'Не удалось обновить профиль', 'danger')
  }
}

async function showToast(message: string, color: string) {
  const toast = await toastController.create({
    message,
    duration: 3000,
    color,
    position: 'top',
  })
  await toast.present()
}
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.profile-content {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* Profile Card - верхняя карточка */
.profile-card {
  background: linear-gradient(135deg, var(--ion-color-primary) 0%, var(--ion-color-primary-shade) 100%);
  padding: 40px 24px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-wrapper:active {
  transform: scale(0.95);
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 5px solid rgba(255, 255, 255, 0.3);
  background: white;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 5px solid rgba(255, 255, 255, 0.3);
}

.avatar-placeholder ion-icon {
  font-size: 64px;
  color: rgba(255, 255, 255, 0.8);
}

.avatar-overlay {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--ion-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.avatar-overlay ion-icon {
  color: var(--ion-color-primary);
  font-size: 24px;
}

.profile-name-display {
  color: white;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-top: 8px;
}

.profile-phone-display {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  text-align: center;
  margin-bottom: 8px;
}

.delete-avatar-btn {
  margin-top: 4px;
  --color: rgba(255, 255, 255, 0.9);
}

/* Edit Form Section */
.edit-section {
  flex: 1;
  background: var(--ion-background-color);
  padding: 24px 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--ion-color-dark);
  margin-bottom: 16px;
  padding: 0 4px;
}

.edit-form {
  background: transparent;
  padding: 0;
}

.edit-form ion-item {
  --background: white;
  --border-radius: 12px;
  --padding-start: 16px;
  --padding-end: 16px;
  --inner-padding-end: 0;
  margin-bottom: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.edit-form ion-item::part(native) {
  border-radius: 12px;
}

.error-message {
  display: block;
  margin: 16px 0;
  padding: 12px 16px;
  background: rgba(235, 68, 90, 0.1);
  border-radius: 12px;
  border-left: 4px solid var(--ion-color-danger);
}

.error-message p {
  margin: 0;
  font-size: 14px;
}

.button-section {
  margin-top: 24px;
  padding: 0 4px;
}

.button-section ion-button {
  --border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.3px;
}
</style>
