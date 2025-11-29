<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card class="login-card">
      <q-card-section class="text-center">
        <div class="text-h4 text-primary q-mb-md">👍 ХичХайк</div>
        <div class="text-h6">Вход в админ-панель</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="handleLogin" class="q-gutter-md">
          <q-input
            v-model="email"
            type="email"
            label="Email"
            outlined
            :rules="[val => !!val || 'Введите email']"
          >
            <template v-slot:prepend>
              <q-icon name="email" />
            </template>
          </q-input>

          <q-input
            v-model="password"
            :type="isPwd ? 'password' : 'text'"
            label="Пароль"
            outlined
            :rules="[val => !!val || 'Введите пароль']"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="isPwd ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd = !isPwd"
              />
            </template>
          </q-input>

          <q-btn
            type="submit"
            label="Войти"
            color="primary"
            class="full-width"
            :loading="loading"
          />
        </q-form>
      </q-card-section>

      <q-separator />

      <q-card-section class="text-center">
        <div class="text-body2 text-grey-7">
          Нет аккаунта?
          <a href="#" @click.prevent="showRegister = true" class="text-primary">
            Зарегистрироваться
          </a>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'LoginPage',

  setup() {
    const $q = useQuasar()
    const router = useRouter()
    const authStore = useAuthStore()

    const email = ref('')
    const password = ref('')
    const isPwd = ref(true)
    const loading = ref(false)
    const showRegister = ref(false)

    const handleLogin = async () => {
      loading.value = true

      const result = await authStore.login(email.value, password.value)

      loading.value = false

      if (result.success) {
        $q.notify({
          type: 'positive',
          message: 'Успешный вход!'
        })
        router.push({ name: 'home' })
      } else {
        $q.notify({
          type: 'negative',
          message: result.error
        })
      }
    }

    return {
      email,
      password,
      isPwd,
      loading,
      showRegister,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login-card {
  width: 100%;
  max-width: 400px;
}
</style>
