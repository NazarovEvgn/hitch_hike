<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          👍 ХичХайк - {{ businessName }}
        </q-toolbar-title>

        <q-btn flat round dense icon="logout" @click="handleLogout">
          <q-tooltip>Выход</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Навигация</q-item-label>

        <q-item clickable :to="{ name: 'home' }" exact>
          <q-item-section avatar>
            <q-icon name="dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Главная</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'bookings' }">
          <q-item-section avatar>
            <q-icon name="event" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Онлайн-записи</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'services' }">
          <q-item-section avatar>
            <q-icon name="build" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Услуги</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'promotions' }">
          <q-item-section avatar>
            <q-icon name="local_offer" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Акции</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'analytics' }">
          <q-item-section avatar>
            <q-icon name="analytics" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Аналитика</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator />

        <q-item clickable :to="{ name: 'profile' }">
          <q-item-section avatar>
            <q-icon name="settings" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Настройки</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const $q = useQuasar()
    const router = useRouter()
    const leftDrawerOpen = ref(false)

    const businessName = computed(() => {
      try {
        const authStore = useAuthStore()
        return authStore.businessName || 'Админ панель'
      } catch (e) {
        return 'Админ панель'
      }
    })

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value
    }

    const handleLogout = () => {
      $q.dialog({
        title: 'Выход',
        message: 'Вы уверены, что хотите выйти?',
        cancel: true,
        persistent: true
      }).onOk(() => {
        try {
          const authStore = useAuthStore()
          authStore.logout()
        } catch (e) {
          console.warn('Logout error:', e)
        }
        router.push({ name: 'login' })
      })
    }

    return {
      leftDrawerOpen,
      businessName,
      toggleLeftDrawer,
      handleLogout
    }
  }
})
</script>
