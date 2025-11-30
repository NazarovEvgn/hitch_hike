import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'map',
    component: () => import('../pages/MapPage.vue')
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('../pages/FavoritesPage.vue')
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('../pages/ErrorNotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
