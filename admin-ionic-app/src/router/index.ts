import { createRouter, createWebHistory } from '@ionic/vue-router'
import { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/authStore'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/features/auth/pages/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/features/dashboard/pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/status',
    name: 'StatusUpdate',
    component: () => import('@/features/business-status/pages/StatusUpdatePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/services',
    name: 'Services',
    component: () => import('@/features/services/pages/ServicesListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/bookings',
    name: 'Bookings',
    component: () => import('@/features/bookings/pages/BookingsListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/features/profile/pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/business-hours',
    name: 'BusinessHours',
    component: () => import('@/features/business-hours/pages/BusinessHoursPage.vue'),
    meta: { requiresAuth: true },
  },
  // Fallback для неизвестных роутов
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

/**
 * Navigation Guard - проверка аутентификации
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false // По умолчанию требуется auth

  console.log('[Router] Navigate to:', to.path)
  console.log('[Router] Requires auth:', requiresAuth)
  console.log('[Router] Is authenticated:', authStore.isAuthenticated)

  if (requiresAuth && !authStore.isAuthenticated) {
    // Требуется авторизация, но пользователь не авторизован
    console.log('[Router] Redirecting to login')
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // Пользователь авторизован и пытается зайти на страницу входа
    console.log('[Router] Already authenticated, redirecting to dashboard')
    next('/dashboard')
  } else {
    // Все ок, пропускаем
    next()
  }
})

export default router
