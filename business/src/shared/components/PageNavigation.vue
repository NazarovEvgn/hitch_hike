<template>
  <div class="page-navigation">
    <!-- Back Button -->
    <ion-button
      v-if="showBackButton"
      fill="clear"
      size="small"
      @click="handleBack"
      class="back-button"
    >
      <ion-icon slot="start" :icon="arrowBackOutline"></ion-icon>
      Назад
    </ion-button>

    <!-- Empty space if no back button -->
    <div v-else></div>

    <!-- Page Title on the right -->
    <h2 class="page-title">{{ pageTitle }}</h2>
  </div>
</template>

<script setup lang="ts">
import { IonButton, IonIcon } from '@ionic/vue'
import { arrowBackOutline } from 'ionicons/icons'
import { useRouter } from 'vue-router'

interface Props {
  pageTitle: string
  showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: true,
})

const router = useRouter()

function handleBack() {
  router.back()
}
</script>

<style scoped>
.page-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--ion-background-color);
  border-bottom: 1px solid var(--ion-color-light-shade);
}

.back-button {
  margin: 0 0 0 8px;
  --padding-start: 4px;
  --padding-end: 0;
}

.page-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--ion-color-dark);
}
</style>
