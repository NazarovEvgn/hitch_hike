import { createRouter, createWebHistory } from '@ionic/vue-router'
import { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/features/auth/pages/LoginPage.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/features/businesses/pages/MapPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/features/businesses/pages/FavoritesPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/features/profile/pages/ProfilePage.vue'),
    meta: { requiresAuth: true }
  },
  // Booking flow routes
  {
    path: '/booking/business/:businessId',
    name: 'BookingBusinessDetails',
    component: () => import('@/features/booking/pages/BusinessDetailsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/booking/select-employee/:businessId/:serviceId',
    name: 'BookingSelectEmployee',
    component: () => import('@/features/booking/pages/SelectEmployeePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/booking/select-date/:businessId/:serviceId/:employeeId',
    name: 'BookingSelectDate',
    component: () => import('@/features/booking/pages/SelectDatePage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard для проверки авторизации
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')

  // Если маршрут требует авторизации и пользователь не авторизован
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
