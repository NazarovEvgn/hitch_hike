import { defineStore } from 'pinia'
import { ref } from 'vue'
import { profileApiService } from '../services/profileApiService'
import type { UserProfile, ProfileUpdateData } from '../types'

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<UserProfile | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProfile() {
    loading.value = true
    error.value = null

    try {
      profile.value = await profileApiService.getProfile()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load profile'
      console.error('Failed to fetch profile:', err)
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: ProfileUpdateData) {
    loading.value = true
    error.value = null

    try {
      profile.value = await profileApiService.updateProfile(data)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update profile'
      console.error('Failed to update profile:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function uploadAvatar(file: File) {
    loading.value = true
    error.value = null

    try {
      profile.value = await profileApiService.uploadAvatar(file)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to upload avatar'
      console.error('Failed to upload avatar:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteAvatar() {
    loading.value = true
    error.value = null

    try {
      profile.value = await profileApiService.deleteAvatar()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete avatar'
      console.error('Failed to delete avatar:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  function clearProfile() {
    profile.value = null
    error.value = null
  }

  return {
    profile,
    loading,
    error,
    fetchProfile,
    updateProfile,
    uploadAvatar,
    deleteAvatar,
    clearProfile,
  }
})
