<template>
  <ion-page>
    <ion-content :fullscreen="true" class="ion-padding">
      <div class="login-container">
        <!-- Лого и заголовок -->
        <div class="login-header">
          <h1 class="ion-text-center">Lets</h1>
        </div>

        <!-- Форма входа -->
        <ion-card class="login-card">
          <ion-card-content>
            <form @submit.prevent="handleLogin">
              <!-- Email -->
              <ion-item lines="full" class="ion-margin-bottom">
                <ion-label position="floating">Email</ion-label>
                <ion-input
                  v-model="email"
                  type="email"
                  required
                  autocomplete="email"
                />
              </ion-item>

              <!-- Пароль -->
              <ion-item lines="full" class="ion-margin-bottom">
                <ion-label position="floating">Пароль</ion-label>
                <ion-input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  autocomplete="current-password"
                />
                <ion-button
                  slot="end"
                  fill="clear"
                  @click="showPassword = !showPassword"
                >
                  <ion-icon :icon="showPassword ? eyeOffOutline : eyeOutline" />
                </ion-button>
              </ion-item>

              <!-- Ошибка -->
              <ion-text v-if="errorMessage" color="danger" class="error-message">
                <p>{{ errorMessage }}</p>
              </ion-text>

              <!-- Кнопка входа -->
              <ion-button
                expand="block"
                type="submit"
                :disabled="loading"
                class="login-button"
              >
                <ion-spinner v-if="loading" name="crescent" />
                <span v-else>Войти</span>
              </ion-button>
            </form>
          </ion-card-content>
        </ion-card>

        <!-- Ссылка на регистрацию (для будущего) -->
        <!--
        <div class="ion-text-center ion-margin-top">
          <ion-text color="medium">
            <p>
              Нет аккаунта?
              <a href="/register" class="register-link">Зарегистрироваться</a>
            </p>
          </ion-text>
        </div>
        -->
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  IonPage,
  IonContent,
  IonCard,
  IonCardContent,
  IonItem,
  IonLabel,
  IonInput,
  IonButton,
  IonText,
  IonIcon,
  IonSpinner,
} from '@ionic/vue'
import { eyeOutline, eyeOffOutline } from 'ionicons/icons'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// Form data
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  // Очищаем предыдущие ошибки
  errorMessage.value = ''

  // Валидация
  if (!email.value || !password.value) {
    errorMessage.value = 'Пожалуйста, заполните все поля'
    return
  }

  loading.value = true

  try {
    const result = await authStore.login({
      email: email.value,
      password: password.value,
    })

    if (result.success) {
      // Успешный вход - редирект на dashboard
      await router.push('/dashboard')
    } else {
      // Ошибка входа
      errorMessage.value = result.error || 'Ошибка входа'
    }
  } catch (error) {
    console.error('[LoginPage] Unexpected error:', error)
    errorMessage.value = 'Произошла непредвиденная ошибка'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  padding: 24px;
}

.login-header {
  margin-bottom: 3rem;
  text-align: center;
}

h1 {
  color: var(--ion-color-primary);
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
  letter-spacing: -0.02em;
}

.login-card {
  width: 100%;
  max-width: 420px;
  margin: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
}

.error-message {
  display: block;
  margin-bottom: 1.5rem;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: rgba(235, 68, 90, 0.1);
  border-left: 3px solid var(--ion-color-danger);
}

.error-message p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-danger);
}

.login-button {
  margin-top: 1.5rem;
  --background: var(--ion-color-primary);
  --border-radius: 8px;
  height: 48px;
  font-weight: 600;
  font-size: 1rem;
}

ion-item {
  --border-radius: 8px;
  --padding-start: 16px;
  --inner-padding-end: 16px;
}

ion-label {
  font-weight: 500;
}
</style>
