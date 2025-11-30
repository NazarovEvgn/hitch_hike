import { boot } from 'quasar/wrappers'
import axios from 'axios'

const api = axios.create({ baseURL: process.env.API_URL || 'http://127.0.0.1:8000/api/v1' })

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
