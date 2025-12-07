import axios, { AxiosInstance } from 'axios'
import config from '../config'

/**
 * API клиент для клиентского приложения (без аутентификации)
 */

export const apiClient: AxiosInstance = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient
