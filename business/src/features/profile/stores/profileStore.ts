import { defineStore } from 'pinia'
import { ref } from 'vue'
import { profileApiService } from '../services/profileApiService'
import type { Business, BusinessUpdateInput } from '../types'

export const useProfileStore = defineStore('profile', () => {
  const business = ref<Business | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProfile(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const data = await profileApiService.getProfile()
      business.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch profile'
      console.error('[ProfileStore] fetchProfile error:', err)
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(
    data: BusinessUpdateInput
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const updated = await profileApiService.updateProfile(data)
      business.value = updated
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update profile'
      console.error('[ProfileStore] updateProfile error:', err)
      return { success: false, error: errorMessage }
    }
  }

  return {
    business,
    loading,
    error,
    fetchProfile,
    updateProfile,
  }
})
