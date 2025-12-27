import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApiService } from '../services/authApiService'
import type { PhoneOTPRequest, OTPVerifyRequest, BusinessLoginRequest } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const userType = ref<'client' | 'business_admin' | null>(
    localStorage.getItem('user_type') as 'client' | 'business_admin' | null
  )

  const isAuthenticated = ref(!!accessToken.value)

  async function devLogin(data: PhoneOTPRequest): Promise<{ success: boolean; error?: string }> {
    try {
      const tokens = await authApiService.devLogin(data)

      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      userType.value = 'client'
      isAuthenticated.value = true

      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      localStorage.setItem('user_type', 'client')

      return { success: true }
    } catch (err: any) {
      console.error('[AuthStore] devLogin error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Login failed'
      }
    }
  }

  async function sendOTP(data: PhoneOTPRequest): Promise<{ success: boolean; error?: string; debugCode?: string }> {
    try {
      const result = await authApiService.sendOTP(data)
      return {
        success: true,
        debugCode: result.debug_code, // MVP only
      }
    } catch (err: any) {
      console.error('[AuthStore] sendOTP error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Failed to send OTP'
      }
    }
  }

  async function verifyOTP(data: OTPVerifyRequest): Promise<{ success: boolean; error?: string }> {
    try {
      const tokens = await authApiService.verifyOTP(data)

      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      userType.value = 'client'
      isAuthenticated.value = true

      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      localStorage.setItem('user_type', 'client')

      return { success: true }
    } catch (err: any) {
      console.error('[AuthStore] verifyOTP error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Invalid OTP code'
      }
    }
  }

  async function loginBusiness(data: BusinessLoginRequest): Promise<{ success: boolean; error?: string }> {
    try {
      const tokens = await authApiService.loginBusiness(data)

      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      userType.value = 'business_admin'
      isAuthenticated.value = true

      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      localStorage.setItem('user_type', 'business_admin')

      return { success: true }
    } catch (err: any) {
      console.error('[AuthStore] loginBusiness error:', err)
      return {
        success: false,
        error: err.response?.data?.detail || 'Invalid credentials'
      }
    }
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    userType.value = null
    isAuthenticated.value = false

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_type')
  }

  return {
    accessToken,
    refreshToken,
    userType,
    isAuthenticated,
    devLogin,
    sendOTP,
    verifyOTP,
    loginBusiness,
    logout,
  }
})
