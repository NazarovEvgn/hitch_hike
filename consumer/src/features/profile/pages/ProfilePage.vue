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

    <ion-content :fullscreen="true" class="ion-padding">
      <!-- Loading -->
      <div v-if="profileStore.loading && !profileStore.profile" class="loading-container">
        <ion-spinner name="crescent"></ion-spinner>
      </div>

      <!-- Profile Form -->
      <div v-else-if="profileStore.profile">
        <!-- Avatar Section -->
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
          <ion-button
            v-if="profileStore.profile.avatar_url"
            fill="clear"
            size="small"
            color="danger"
            @click="handleDeleteAvatar"
          >
            Удалить фото
          </ion-button>
        </div>

        <!-- Form -->
        <ion-list>
          <ion-item>
            <ion-label position="floating">Имя *</ion-label>
            <ion-input v-model="formData.name" type="text" required></ion-input>
          </ion-item>

          <ion-item>
            <ion-label position="floating">Пол</ion-label>
            <ion-select v-model="formData.gender" placeholder="Выберите">
              <ion-select-option value="male">Мужской</ion-select-option>
              <ion-select-option value="female">Женский</ion-select-option>
              <ion-select-option value="other">Другой</ion-select-option>
            </ion-select>
          </ion-item>

          <ion-item>
            <ion-label position="floating">Телефон</ion-label>
            <ion-input :value="profileStore.profile.phone" type="tel" disabled></ion-input>
            <ion-note slot="helper">Номер телефона используется для входа</ion-note>
          </ion-item>

          <ion-item>
            <ion-label position="floating">Email</ion-label>
            <ion-input v-model="formData.email" type="email"></ion-input>
          </ion-item>
        </ion-list>

        <!-- Error Message -->
        <ion-text v-if="profileStore.error" color="danger" class="error-message">
          <p>{{ profileStore.error }}</p>
        </ion-text>

        <!-- Save Button -->
        <ion-button
          expand="block"
          :disabled="profileStore.loading || !isFormValid"
          @click="handleSave"
          class="save-button"
        >
          <ion-spinner v-if="profileStore.loading" name="crescent" />
          <span v-else>Сохранить изменения</span>
        </ion-button>
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

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  cursor: pointer;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--ion-color-primary);
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--ion-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--ion-color-primary);
}

.avatar-placeholder ion-icon {
  font-size: 48px;
  color: var(--ion-color-medium);
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--ion-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--ion-background-color);
}

.avatar-overlay ion-icon {
  color: white;
  font-size: 20px;
}

.error-message {
  display: block;
  margin: 16px 0;
  padding: 12px;
  background: rgba(235, 68, 90, 0.1);
  border-radius: 8px;
}

.error-message p {
  margin: 0;
}

.save-button {
  margin-top: 24px;
}
</style>
