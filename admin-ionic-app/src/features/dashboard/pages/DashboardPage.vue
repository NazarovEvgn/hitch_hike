<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-menu-button />
        </ion-buttons>
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

        <!-- Быстрые действия -->
        <ion-card>
          <ion-card-header>
            <ion-card-title>Быстрые действия</ion-card-title>
          </ion-card-header>
          <ion-card-content>
            <ion-list>
              <ion-item button detail @click="router.push('/status')">
                <ion-icon slot="start" :icon="timeOutline" color="primary" />
                <ion-label>
                  <h2>Обновить статус</h2>
                  <p>Изменить доступность</p>
                </ion-label>
              </ion-item>

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
import { computed } from 'vue'
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
  IonMenuButton,
} from '@ionic/vue'
import {
  logOutOutline,
  timeOutline,
  calendarOutline,
  pricetagOutline,
} from 'ionicons/icons'
import { useAuthStore } from '@/features/auth/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

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
}
</style>
