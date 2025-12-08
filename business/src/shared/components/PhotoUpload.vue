<template>
  <div class="photo-upload">
    <!-- Photo Preview -->
    <div v-if="photoUrl" class="photo-preview">
      <img :src="fullPhotoUrl" alt="Photo preview" />
      <ion-button
        fill="clear"
        color="danger"
        class="delete-button"
        @click="handleDelete"
        :disabled="uploading"
      >
        <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
      </ion-button>
    </div>

    <!-- Upload Placeholder -->
    <div v-else class="upload-placeholder" @click="triggerFileInput">
      <ion-icon :icon="cameraOutline" size="large"></ion-icon>
      <span>{{ label }}</span>
      <ion-spinner v-if="uploading" name="crescent"></ion-spinner>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/jpg,image/png,image/webp"
      @change="handleFileSelect"
      style="display: none"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { IonButton, IonIcon, IonSpinner } from '@ionic/vue'
import { cameraOutline, trashOutline } from 'ionicons/icons'
import apiClient from '@/core/api/client'

interface Props {
  modelValue: string | null
  label?: string
}

interface Emits {
  (e: 'update:modelValue', value: string | null): void
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Добавить фото',
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)

const photoUrl = computed(() => props.modelValue)

const fullPhotoUrl = computed(() => {
  if (!photoUrl.value) return ''
  // If it's already a full URL, return as is
  if (photoUrl.value.startsWith('http')) return photoUrl.value
  // Otherwise prepend API base URL
  return `${import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '')}${photoUrl.value}`
})

function triggerFileInput() {
  if (uploading.value) return
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // Validate file size (5MB max)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    alert('Файл слишком большой. Максимальный размер: 5MB')
    return
  }

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    alert('Неподдерживаемый формат файла. Разрешены: JPG, PNG, WebP')
    return
  }

  // Upload file
  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post('/upload/photo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Emit the URL
    emit('update:modelValue', response.data.url)
  } catch (error: any) {
    console.error('Photo upload error:', error)
    alert(error.response?.data?.detail || 'Ошибка загрузки фото')
  } finally {
    uploading.value = false
    // Reset input
    if (target) target.value = ''
  }
}

async function handleDelete() {
  if (!photoUrl.value || uploading.value) return

  if (!confirm('Удалить фото?')) return

  uploading.value = true

  try {
    await apiClient.delete('/upload/photo', {
      params: { url: photoUrl.value },
    })

    // Clear the photo URL
    emit('update:modelValue', null)
  } catch (error: any) {
    console.error('Photo delete error:', error)
    alert(error.response?.data?.detail || 'Ошибка удаления фото')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.photo-upload {
  width: 100%;
}

.photo-preview {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--ion-color-light);
}

.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-button {
  position: absolute;
  top: 8px;
  right: 8px;
  --background: rgba(255, 255, 255, 0.9);
  --border-radius: 50%;
  width: 40px;
  height: 40px;
}

.upload-placeholder {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  background: var(--ion-color-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.upload-placeholder:hover {
  background: var(--ion-color-light-shade);
}

.upload-placeholder ion-icon {
  font-size: 48px;
  color: var(--ion-color-medium);
}

.upload-placeholder span {
  font-size: 0.9rem;
  color: var(--ion-color-medium);
}

.upload-placeholder ion-spinner {
  margin-top: 8px;
}
</style>
