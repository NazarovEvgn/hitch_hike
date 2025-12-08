<template>
  <ion-page>
    <AppHeader>
      <template #actions>
        <ion-button @click="handleLogout">
          <ion-icon slot="icon-only" :icon="logOutOutline" />
        </ion-button>
      </template>
    </AppHeader>

    <ion-content class="ion-padding">
      <PageNavigation page-title="Главная" :show-back-button="false" />
      <div class="dashboard-container">
        <!-- Статус доступности -->
        <ion-card>
          <ion-card-content>
            <div class="status-toggle-container">
              <label class="status-label">
                Включить статус "Свободны"
              </label>

              <ion-toggle
                v-model="isAvailable"
                :disabled="statusStore.loading"
                color="success"
                @ionChange="handleStatusToggle"
              ></ion-toggle>
            </div>
          </ion-card-content>
        </ion-card>

        <!-- Быстрые действия -->
        <ion-card>
          <ion-card-content>
            <ion-list>

              <ion-item button detail @click="router.push('/bookings')">
                <ion-icon slot="start" :icon="calendarOutline" color="primary" />
                <ion-label>
                  <h2>Онлайн-записи</h2>
                  <p>Управление бронированиями</p>
                </ion-label>
              </ion-item>

              <ion-item button detail @click="router.push('/services')">
                <ion-icon slot="start" :icon="pricetagOutline" color="primary" />
                <ion-label>
                  <h2>Услуги и цены</h2>
                  <p>Редактировать прайс</p>
                </ion-label>
              </ion-item>

              <ion-item button detail @click="router.push('/profile')">
                <ion-icon slot="start" :icon="personOutline" color="primary" />
                <ion-label>
                  <h2>Профиль</h2>
                  <p>Настройки бизнеса</p>
                </ion-label>
              </ion-item>

              <ion-item button detail @click="router.push('/business-hours')">
                <ion-icon slot="start" :icon="timeOutline" color="primary" />
                <ion-label>
                  <h2>Часы работы</h2>
                  <p>Расписание на неделю</p>
                </ion-label>
              </ion-item>
            </ion-list>
          </ion-card-content>
        </ion-card>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonContent,
  IonCard,
  IonCardContent,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonButton,
  IonToggle,
  toastController,
} from '@ionic/vue'
import {
  logOutOutline,
  calendarOutline,
  pricetagOutline,
  personOutline,
  timeOutline,
} from 'ionicons/icons'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useStatusStore } from '@/features/business-status/stores/statusStore'
import AppHeader from '@/shared/components/AppHeader.vue'
import PageNavigation from '@/shared/components/PageNavigation.vue'

const router = useRouter()
const authStore = useAuthStore()
const statusStore = useStatusStore()

const isAvailable = ref(false)

// Load current status on mount
onMounted(async () => {
  await statusStore.fetchCurrentStatus()
  isAvailable.value = statusStore.status === 'available'
})

// Handle status toggle
async function handleStatusToggle() {
  const value = isAvailable.value

  const result = await statusStore.updateStatus({
    status: value ? 'available' : 'busy',
    estimated_wait_minutes: 0,
  })

  if (result.success) {
    const toast = await toastController.create({
      message: value
        ? 'Статус "Свободны" включен - клиенты увидят зеленый маячок на карте'
        : 'Статус "Свободны" выключен',
      duration: 2500,
      color: value ? 'success' : 'medium',
      position: 'top',
    })
    await toast.present()
  } else {
    // Revert toggle on error
    isAvailable.value = !value
    const toast = await toastController.create({
      message: result.error || 'Ошибка обновления статуса',
      duration: 3000,
      color: 'danger',
      position: 'top',
    })
    await toast.present()
  }
}

// Actions
async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  max-width: 800px;
  margin: 0 auto;
}

ion-card {
  margin-bottom: 1rem;
  border-radius: 12px;
  overflow: hidden;
}

/* Status Toggle Container */
.status-toggle-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 4px 0;
}

.status-label {
  font-size: 1rem;
  font-weight: 500;
  color: var(--ion-color-dark);
}
</style>
