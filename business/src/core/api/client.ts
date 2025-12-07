import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import config from '../config'

/**
 * API клиент с JWT аутентификацией
 */

// Создаем экземпляр axios
export const apiClient: AxiosInstance = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request Interceptor - добавляет JWT токен к каждому запросу
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor - обрабатывает ошибки 401 и обновляет токен
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Если получили 401 и еще не пытались обновить токен
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          // Пытаемся обновить access token
          const response = await axios.post(
            `${config.apiBaseUrl}/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token } = response.data
          localStorage.setItem('accessToken', access_token)

          // Повторяем оригинальный запрос с новым токеном
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Если обновление токена не удалось - выходим из системы
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')

          // Редирект на страницу входа
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }

          return Promise.reject(refreshError)
        }
      } else {
        // Нет refresh token - редирект на логин
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
