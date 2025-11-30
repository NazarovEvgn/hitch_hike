import { createApp } from 'vue'
import { Quasar, Notify, Dialog, Loading, LocalStorage } from 'quasar'
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

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Notify,
    Dialog,
    Loading,
    LocalStorage
  }
})

const pinia = createPinia()
app.use(pinia)
app.use(router)

// Boot axios
axios({ app })

app.mount('#q-app')
