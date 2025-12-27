<template>
  <ion-page>
    <ion-content :fullscreen="true" class="ion-padding">
      <div class="login-container">
        <!-- Лого и заголовок -->
        <div class="login-header">
          <h1 class="ion-text-center">Lets</h1>
        </div>

        <!-- Основная форма: Passwordless вход для клиентов -->
        <ion-card class="login-card">
          <ion-card-content>

            <!-- DEV MODE: Упрощенный вход по телефону без кода -->
            <form @submit.prevent="handleDevLogin">
              <ion-item lines="full" class="ion-margin-bottom">
                <ion-label position="floating">Номер телефона</ion-label>
                <ion-input
                  v-model="clientPhone"
                  type="tel"
                  placeholder="+7 (999) 123-45-67"
                  required
                  autocomplete="tel"
                />
              </ion-item>

              <ion-text v-if="clientError" color="danger" class="error-message">
                <p>{{ clientError }}</p>
              </ion-text>

              <ion-button
                expand="block"
                type="submit"
                :disabled="clientLoading"
                class="login-button"
              >
                <ion-spinner v-if="clientLoading" name="crescent" />
                <span v-else>Войти</span>
              </ion-button>

              <ion-text color="medium" class="dev-mode-note">
                <p>Режим разработки: вход без кода подтверждения</p>
              </ion-text>
            </form>
          </ion-card-content>
        </ion-card>

        <!-- Раскрывающийся блок: Вход для бизнеса -->
        <div class="business-login-container">
          <ion-accordion-group>
            <ion-accordion value="business-login">
              <ion-item slot="header" color="light" class="business-header">
                <ion-label>
                  <h3>Вход для бизнеса</h3>
                </ion-label>
              </ion-item>

              <div class="ion-padding business-content" slot="content">
                <form @submit.prevent="handleBusinessLogin">
                  <!-- Email -->
                  <ion-item lines="full" class="ion-margin-bottom">
                    <ion-label position="floating">Email</ion-label>
                    <ion-input
                      v-model="businessEmail"
                      type="email"
                      required
                      autocomplete="email"
                    />
                  </ion-item>

                  <!-- Пароль -->
                  <ion-item lines="full" class="ion-margin-bottom">
                    <ion-label position="floating">Пароль</ion-label>
                    <ion-input
                      v-model="businessPassword"
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
                  <ion-text v-if="businessError" color="danger" class="error-message">
                    <p>{{ businessError }}</p>
                  </ion-text>

                  <!-- Кнопка входа -->
                  <ion-button
                    expand="block"
                    type="submit"
                    :disabled="businessLoading"
                    class="login-button"
                  >
                    <ion-spinner v-if="businessLoading" name="crescent" />
                    <span v-else>Войти</span>
                  </ion-button>

                  <!-- Ссылка на регистрацию -->
                  <div class="register-link-container">
                    <ion-text color="medium">
                      <p>
                        Нет аккаунта?
                        <a href="/register" class="register-link">Зарегистрироваться</a>
                      </p>
                    </ion-text>
                  </div>
                </form>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </div>
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
  IonAccordion,
  IonAccordionGroup,
} from '@ionic/vue'
import { eyeOutline, eyeOffOutline } from 'ionicons/icons'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// Client (passwordless) login state
const clientPhone = ref('')
const clientLoading = ref(false)
const clientError = ref('')

// Business login state
const businessEmail = ref('')
const businessPassword = ref('')
const showPassword = ref(false)
const businessLoading = ref(false)
const businessError = ref('')

async function handleDevLogin() {
  clientError.value = ''
  clientLoading.value = true

  const result = await authStore.devLogin({ phone: clientPhone.value })

  clientLoading.value = false

  if (result.success) {
    // Редирект на главную страницу клиента
    await router.push('/map')
  } else {
    clientError.value = result.error || 'Ошибка входа'
  }
}

async function handleBusinessLogin() {
  businessError.value = ''
  businessLoading.value = true

  const result = await authStore.loginBusiness({
    email: businessEmail.value,
    password: businessPassword.value,
  })

  businessLoading.value = false

  if (result.success) {
    // Редирект на админ-панель бизнеса (external app на порту 5173)
    window.location.href = 'http://localhost:5173/dashboard'
  } else {
    businessError.value = result.error || 'Неверный email или пароль'
  }
}
</script>

<style scoped>
ion-content {
  --background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  padding: 24px;
}

.login-header {
  margin-bottom: 2rem;
  text-align: center;
}

h1 {
  color: #000000;
  font-weight: 700;
  font-size: 3rem;
  margin: 0;
  letter-spacing: -0.02em;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.login-card {
  width: 100%;
  max-width: 420px;
  margin: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

ion-card-content {
  padding: 32px 24px;
}

ion-item {
  --background: #ffffff;
  --border-radius: 12px;
  --padding-start: 16px;
  --inner-padding-end: 16px;
  --border-width: 1px;
  --border-color: var(--ion-color-light-shade);
  margin-bottom: 16px;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

ion-item:focus-within {
  --border-color: var(--ion-color-primary);
  --border-width: 2px;
}

ion-label {
  font-weight: 500;
  --color: var(--ion-color-dark);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

ion-input {
  --color: var(--ion-color-dark);
  --placeholder-color: var(--ion-color-medium);
  font-size: 1rem;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.error-message {
  display: block;
  margin-bottom: 1rem;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: var(--ion-color-danger-tint);
  border-left: 3px solid var(--ion-color-danger);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.error-message p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ion-color-danger);
}

.otp-sent-message {
  display: block;
  margin-bottom: 1rem;
  text-align: center;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.otp-sent-message p {
  margin: 0;
  font-size: 0.9rem;
}

.debug-code {
  display: block;
  margin-bottom: 1rem;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: var(--ion-color-success-tint);
  border-left: 3px solid var(--ion-color-success);
  text-align: center;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.debug-code p {
  margin: 0;
  font-size: 0.9rem;
}

.login-button {
  margin-top: 1rem;
  --background: var(--ion-color-primary);
  --border-radius: 12px;
  height: 52px;
  font-weight: 600;
  font-size: 1rem;
  text-transform: none;
  letter-spacing: 0.02em;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.login-button:hover {
  opacity: 0.9;
}

.dev-mode-note {
  display: block;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.85rem;
  opacity: 0.7;
}

.dev-mode-note p {
  margin: 0;
}

/* Бизнес логин */
.business-login-container {
  width: 100%;
  max-width: 420px;
  margin-top: 1.5rem;
}

.business-login-container ion-accordion-group {
  border: 2px solid var(--ion-color-medium-tint);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
}

.business-login-container ion-accordion-group:hover {
  border-color: var(--ion-color-primary);
  box-shadow: 0 4px 12px rgba(39, 18, 106, 0.15);
}

.business-header {
  --border-radius: 0;
  cursor: pointer;
}

.business-header ion-label h3 {
  margin: 0;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--ion-color-dark);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.business-content {
  background: rgba(255, 255, 255, 0.95);
}

.register-link-container {
  margin-top: 1rem;
  text-align: center;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.register-link-container p {
  margin: 0;
  font-size: 0.9rem;
}

.register-link {
  color: var(--ion-color-primary);
  text-decoration: none;
  font-weight: 600;
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}

.register-link:hover {
  text-decoration: underline;
}

ion-button[fill="clear"] {
  --color: var(--ion-color-primary);
  font-family: 'Tilda Sans', -apple-system, system-ui, sans-serif;
}
</style>
