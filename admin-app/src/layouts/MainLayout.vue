<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <div class="column">
            <div class="text-weight-medium">{{ businessName || 'Загрузка...' }}</div>
            <div class="text-caption">{{ businessAddress || '' }}</div>
          </div>
        </q-toolbar-title>

        <q-btn flat round dense icon="logout" @click="handleLogout">
          <q-tooltip>Выход</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" bordered>
      <q-list>
        <q-item-label header>Меню</q-item-label>

        <q-item clickable :to="{ name: 'home' }">
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Главная</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'profile' }">
          <q-item-section avatar>
            <q-icon name="account_circle" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Личный кабинет</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable :to="{ name: 'services' }">
          <q-item-section avatar>
            <q-icon name="build" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Услуги и цены</q-item-label>
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
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const $q = useQuasar()
    const router = useRouter()
    const leftDrawerOpen = ref(false)
    const businessName = ref('')
    const businessAddress = ref('')
    let authStore = null

    onMounted(async () => {
      try {
        // Dynamic import to ensure Pinia is ready
        const { useAuthStore } = await import('../stores/auth')
        authStore = useAuthStore()
        businessName.value = authStore.businessName
        businessAddress.value = authStore.businessAddress

        // Watch for changes
        const unwatch = () => {
          businessName.value = authStore.businessName
          businessAddress.value = authStore.businessAddress
        }

        // Update every second to catch changes
        const interval = setInterval(unwatch, 1000)

        // Cleanup on unmount
        return () => clearInterval(interval)
      } catch (error) {
        console.error('Failed to load auth store:', error)
      }
    })

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value
    }

    const handleLogout = async () => {
      $q.dialog({
        title: 'Выход',
        message: 'Вы уверены, что хотите выйти?',
        cancel: true,
        persistent: true
      }).onOk(async () => {
        try {
          if (!authStore) {
            const { useAuthStore } = await import('../stores/auth')
            authStore = useAuthStore()
          }
          authStore.logout()
          router.push({ name: 'login' })
        } catch (error) {
          console.error('Logout error:', error)
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          router.push({ name: 'login' })
        }
      })
    }

    return {
      leftDrawerOpen,
      businessName,
      businessAddress,
      toggleLeftDrawer,
      handleLogout
    }
  }
})
</script>
