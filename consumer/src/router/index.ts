import { createRouter, createWebHistory } from '@ionic/vue-router'
import { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/map'
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('@/features/businesses/pages/MapPage.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/features/businesses/pages/FavoritesPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
