<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-title>{{ businessName || 'Dashboard' }}</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="handleLogout">
            <ion-icon slot="icon-only" :icon="logOutOutline" />
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="dashboard-container">
        <!-- Информация о бизнесе -->
        <ion-card v-if="business">
          <ion-card-header>
            <ion-card-title>{{ business.name }}</ion-card-title>
            <ion-card-subtitle>{{ business.address }}</ion-card-subtitle>
          </ion-card-header>
          <ion-card-content>
            <p><strong>Тип:</strong> {{ businessTypeLabel }}</p>
            <p><strong>Телефон:</strong> {{ business.phone }}</p>
          </ion-card-content>
        </ion-card>

        <!-- Статус доступности -->
        <ion-card>
          <ion-card-content>
            <div class="status-toggle-container">
              <label for="status-switch" class="status-label">
                Включить статус "Свободны"
              </label>

              <Switch
                id="status-switch"
                v-model="isAvailable"
                :disabled="statusStore.loading"
                :style="{
                  position: 'relative',
                  display: 'inline-flex',
                  alignItems: 'center',
                  height: '31px',
                  width: '51px',
                  flexShrink: 0,
                  cursor: statusStore.loading ? 'not-allowed' : 'pointer',
                  borderRadius: '9999px',
                  padding: '2px',
                  transition: 'all 0.2s ease-in-out',
                  boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.15)',
                  backgroundColor: isAvailable ? '#98EA14' : '#e5e7eb',
                  border: isAvailable ? '1px solid #8bd612' : '1px solid #d1d5db',
                  opacity: statusStore.loading ? 0.5 : 1
                }"
                @update:modelValue="handleStatusToggle"
              >
                <span class="sr-only">Включить статус "Свободны"</span>
                <span
                  :style="{
                    pointerEvents: 'none',
                    display: 'inline-block',
                    height: '27px',
                    width: '27px',
                    borderRadius: '9999px',
                    backgroundColor: 'white',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.1)',
                    transition: 'transform 0.2s ease-in-out',
                    transform: isAvailable ? 'translateX(20px)' : 'translateX(0)'
                  }"
                />
              </Switch>
            </div>
          </ion-card-content>
        </ion-card>

        <!-- Быстрые действия -->
        <ion-card>
          <ion-card-header>
            <ion-card-title>Быстрые действия</ion-card-title>
          </ion-card-header>
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

        <!-- Информационное сообщение -->
        <ion-card color="light">
          <ion-card-content>
            <p class="ion-text-center">
              🚧 Страница в разработке. Функционал будет добавлен позже.
            </p>
          </ion-card-content>
        </ion-card>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardSubtitle,
  IonCardContent,
  IonList,
  IonItem,
  IonLabel,
  IonIcon,
  IonButtons,
  IonButton,
  toastController,
} from '@ionic/vue'
import {
  logOutOutline,
  calendarOutline,
  pricetagOutline,
  personOutline,
  timeOutline,
} from 'ionicons/icons'
import { Switch } from '@headlessui/vue'
import { useAuthStore } from '@/features/auth/stores/authStore'
import { useStatusStore } from '@/features/business-status/stores/statusStore'

const router = useRouter()
const authStore = useAuthStore()
const statusStore = useStatusStore()

const isAvailable = ref(false)

// Computed
const businessName = computed(() => authStore.businessName)
const business = computed(() => authStore.business)

const businessTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    car_wash: 'Автомойка',
    auto_repair: 'Автосервис',
    tire_service: 'Шиномонтаж',
    beauty_salon: 'Салон красоты',
  }
  return business.value ? typeMap[business.value.business_type] || business.value.business_type : ''
})

// Load current status on mount
onMounted(async () => {
  await statusStore.fetchCurrentStatus()
  isAvailable.value = statusStore.status === 'available'
})

// Handle status toggle
async function handleStatusToggle(value: boolean) {
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
  cursor: pointer;
  user-select: none;
}

/* iOS-style Toggle Switch */
.status-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  height: 31px;
  width: 51px;
  flex-shrink: 0;
  cursor: pointer;
  border-radius: 9999px;
  padding: 2px;
  transition: all 0.2s ease-in-out;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.15);
}

/* Switch ON state - зеленый */
.status-switch.switch-on {
  background-color: #98EA14;
  border: 1px solid #8bd612;
}

/* Switch OFF state - серый */
.status-switch.switch-off {
  background-color: #e5e7eb;
  border: 1px solid #d1d5db;
}

.status-switch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-switch:focus {
  outline: 2px solid #27126A;
  outline-offset: 2px;
}

.switch-thumb {
  pointer-events: none;
  display: inline-block;
  height: 27px;
  width: 27px;
  border-radius: 9999px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}

/* Thumb positions */
.switch-thumb.thumb-off {
  transform: translateX(0);
}

.switch-thumb.thumb-on {
  transform: translateX(20px);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
