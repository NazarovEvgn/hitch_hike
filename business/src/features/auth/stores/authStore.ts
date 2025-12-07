import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/core/api/client'
import type {
  LoginCredentials,
  BusinessRegistrationData,
  BusinessProfile,
  User,
  AuthResult,
  AuthResponse,
} from '../types'

/**
 * Pinia Store для аутентификации и управления бизнес-профилем
 */
export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const business = ref<BusinessProfile | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const businessName = computed(() => business.value?.name || '')
  const businessAddress = computed(() => business.value?.address || '')

  // Actions
  async function login(credentials: LoginCredentials): Promise<AuthResult> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login/business', credentials)
      const { access_token, refresh_token } = response.data

      // Сохраняем токены
      accessToken.value = access_token
      refreshToken.value = refresh_token
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      // Загружаем профиль бизнеса
      await fetchProfile()

      return { success: true }
    } catch (error: any) {
      console.error('[AuthStore] Login error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Ошибка входа',
      }
    }
  }

  async function register(data: BusinessRegistrationData): Promise<AuthResult> {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register/business', data)
      const { access_token, refresh_token } = response.data

      // Сохраняем токены
      accessToken.value = access_token
      refreshToken.value = refresh_token
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)

      // Загружаем профиль бизнеса
      await fetchProfile()

      return { success: true }
    } catch (error: any) {
      console.error('[AuthStore] Register error:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Ошибка регистрации',
      }
    }
  }

  async function fetchProfile(): Promise<void> {
    try {
      console.log('[AuthStore] Fetching business profile...')
      const response = await apiClient.get<BusinessProfile>('/admin/business/profile')
      business.value = response.data
      console.log('[AuthStore] Business profile loaded:', business.value)
    } catch (error: any) {
      console.error('[AuthStore] Fetch profile error:', error)
      // Не бросаем ошибку - профиль может быть не обязательным при первом входе
    }
  }

  function logout(): void {
    // Очищаем state
    user.value = null
    business.value = null
    accessToken.value = null
    refreshToken.value = null

    // Очищаем localStorage
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')

    console.log('[AuthStore] Logged out')
  }

  return {
    // State
    user,
    business,
    accessToken,
    refreshToken,

    // Getters
    isAuthenticated,
    businessName,
    businessAddress,

    // Actions
    login,
    register,
    fetchProfile,
    logout,
  }
})
