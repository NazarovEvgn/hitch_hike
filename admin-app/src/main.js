import { createApp } from 'vue'
import { Quasar, Notify, Dialog, Loading } from 'quasar'
import { createPinia } from 'pinia'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/roboto-font/roboto-font.css'

// Import Quasar css
import 'quasar/dist/quasar.css'

// Import app styles
import './css/app.scss'

import App from './App.vue'
import router from './router'
import axios from './boot/axios'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Notify,
    Dialog,
    Loading
  }
})

const pinia = createPinia()
app.use(pinia)

// Setup router guards after Pinia is initialized
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

app.use(router)

// Boot axios
axios({ app })

app.mount('#q-app')
