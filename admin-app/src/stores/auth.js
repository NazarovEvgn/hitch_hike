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
    businessName: (state) => state.business?.name || ''
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
        const response = await api.get('/admin/business/profile')
        this.business = response.data
      } catch (error) {
        console.error('Failed to fetch profile:', error)
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
