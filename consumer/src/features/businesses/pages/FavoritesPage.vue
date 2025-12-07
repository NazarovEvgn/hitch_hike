<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <ion-buttons slot="start">
          <ion-back-button default-href="/map"></ion-back-button>
        </ion-buttons>
        <ion-title>Избранное</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <!-- Empty State -->
      <div v-if="favorites.length === 0" class="empty-state">
        <ion-icon :icon="heartOutline" size="large" color="medium"></ion-icon>
        <p>Нет избранных бизнесов</p>
        <ion-button @click="router.push('/map')">
          Найти бизнесы
        </ion-button>
      </div>

      <!-- Favorites List -->
      <ion-list v-else>
        <ion-item-sliding v-for="business in favorites" :key="business.id">
          <ion-item button @click="selectBusiness(business)">
            <div class="business-card">
              <div class="business-header">
                <div class="business-info">
                  <h3>{{ business.name }}</h3>
                  <p class="business-type">{{ businessTypeLabel(business.business_type) }}</p>
                </div>
              </div>

              <div class="business-details">
                <div class="detail-row">
                  <ion-icon :icon="locationOutline" color="medium"></ion-icon>
                  <span>{{ business.address }}</span>
                </div>
                <div class="detail-row">
                  <ion-icon :icon="callOutline" color="medium"></ion-icon>
                  <span>{{ business.phone }}</span>
                </div>
              </div>
            </div>
          </ion-item>

          <ion-item-options>
            <ion-item-option color="danger" @click="removeFavorite(business.id)">
              <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
            </ion-item-option>
          </ion-item-options>
        </ion-item-sliding>
      </ion-list>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonButtons,
  IonBackButton,
  IonTitle,
  IonContent,
  IonList,
  IonItem,
  IonItemSliding,
  IonItemOptions,
  IonItemOption,
  IonIcon,
  IonButton,
} from '@ionic/vue'
import {
  heartOutline,
  locationOutline,
  callOutline,
  trashOutline,
} from 'ionicons/icons'
import type { Business, BusinessType } from '../types'

const router = useRouter()

const favorites = ref<Business[]>([])

onMounted(() => {
  loadFavorites()
})

function loadFavorites() {
  const stored = localStorage.getItem('favorites')
  if (stored) {
    favorites.value = JSON.parse(stored)
  }
}

function removeFavorite(id: number) {
  favorites.value = favorites.value.filter(b => b.id !== id)
  localStorage.setItem('favorites', JSON.stringify(favorites.value))
}

function selectBusiness(business: Business) {
  // Navigate to map and select business
  router.push('/map')
}

function businessTypeLabel(type: BusinessType): string {
  const labels = {
    car_wash: 'Автомойка',
    auto_repair: 'Автосервис',
    tire_service: 'Шиномонтаж',
    beauty_salon: 'Салон красоты',
  }
  return labels[type] || type
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  padding: 24px;
}

.empty-state p {
  color: var(--ion-color-medium);
  margin: 0;
}

.empty-state ion-icon {
  font-size: 64px;
}

.business-card {
  width: 100%;
  padding: 12px 0;
}

.business-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.business-info h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.business-type {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-medium);
}

.business-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
}

.detail-row ion-icon {
  font-size: 18px;
}
</style>
