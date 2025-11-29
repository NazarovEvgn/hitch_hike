import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'

const router = createRouter({
  history: createWebHistory(process.env.VUE_ROUTER_BASE || '/'),
  routes
})

export default router
