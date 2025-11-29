const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/LoginPage.vue')
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../pages/DashboardPage.vue')
      },
      {
        path: 'status',
        name: 'status',
        component: () => import('../pages/StatusPage.vue')
      },
      {
        path: 'services',
        name: 'services',
        component: () => import('../pages/ServicesPage.vue')
      },
      {
        path: 'bookings',
        name: 'bookings',
        component: () => import('../pages/BookingsPage.vue')
      },
      {
        path: 'promotions',
        name: 'promotions',
        component: () => import('../pages/PromotionsPage.vue')
      },
      {
        path: 'analytics',
        name: 'analytics',
        component: () => import('../pages/AnalyticsPage.vue')
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../pages/ProfilePage.vue')
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue')
  }
]

export default routes
