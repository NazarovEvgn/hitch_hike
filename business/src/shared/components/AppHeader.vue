<template>
  <ion-header>
    <ion-toolbar color="primary">
      <!-- Business Info with Avatar -->
      <div class="header-business-info">
        <!-- Avatar -->
        <div class="business-avatar">
          <img v-if="logoUrl" :src="fullLogoUrl" :alt="businessName" />
          <ion-icon v-else :icon="businessOutline" size="large"></ion-icon>
        </div>

        <!-- Name and Address -->
        <div class="business-text">
          <h1 class="business-name">{{ businessName || 'Загрузка...' }}</h1>
          <p class="business-address">{{ businessAddress || '' }}</p>
        </div>
      </div>

      <!-- Action Buttons (слот для кнопок) -->
      <ion-buttons slot="end">
        <slot name="actions"></slot>
      </ion-buttons>
    </ion-toolbar>
  </ion-header>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { IonHeader, IonToolbar, IonButtons, IonIcon } from '@ionic/vue'
import { businessOutline } from 'ionicons/icons'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useProfileStore } from '@/features/profile/stores/profileStore'

const authStore = useAuthStore()
const profileStore = useProfileStore()

// Load profile on mount if not loaded
onMounted(() => {
  if (!profileStore.business) {
    profileStore.fetchProfile()
  }
})

const businessName = computed(() => authStore.businessName)
const businessAddress = computed(() => authStore.businessAddress)
const logoUrl = computed(() => profileStore.business?.logo_url)

// Get full logo URL
const fullLogoUrl = computed(() => {
  if (!logoUrl.value) return ''
  if (logoUrl.value.startsWith('http')) return logoUrl.value
  // Remove /api/v1 suffix to get base URL for static files
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
  const baseUrl = apiUrl.replace('/api/v1', '')
  return `${baseUrl}${logoUrl.value}`
})
</script>

<style scoped>
.header-business-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
}

.business-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.business-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.business-avatar ion-icon {
  color: white;
  font-size: 28px;
}

.business-text {
  flex: 1;
  min-width: 0;
}

.business-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.business-address {
  margin: 2px 0 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
