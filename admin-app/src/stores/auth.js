import { defineStore } from 'pinia'
import { api } from '../boot/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    business: null,
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    businessName: (state) => state.business?.name || '',
    businessAddress: (state) => state.business?.address || ''
  },

  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/auth/login/business', { email, password })
        const { access_token, refresh_token } = response.data

        this.accessToken = access_token
        this.refreshToken = refresh_token

        localStorage.setItem('accessToken', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        await this.fetchProfile()

        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Ошибка входа'
        }
      }
    },

    async register(data) {
      try {
        const response = await api.post('/auth/register/business', data)
        const { access_token, refresh_token } = response.data

        this.accessToken = access_token
        this.refreshToken = refresh_token

        localStorage.setItem('accessToken', access_token)
        localStorage.setItem('refreshToken', refresh_token)

        await this.fetchProfile()

        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Ошибка регистрации'
        }
      }
    },

    async fetchProfile() {
      try {
        console.log('[fetchProfile] Starting...')
        const response = await api.get('/admin/business/profile')
        console.log('[fetchProfile] Response received:', response.data)
        this.business = response.data
        console.log('[fetchProfile] Business set in store:', this.business)
        console.log('[fetchProfile] Business name:', this.business?.name)
        console.log('[fetchProfile] Business address:', this.business?.address)
      } catch (error) {
        console.error('[fetchProfile] Error:', error)
      }
    },

    logout() {
      this.user = null
      this.business = null
      this.accessToken = null
      this.refreshToken = null

      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
  }
})
