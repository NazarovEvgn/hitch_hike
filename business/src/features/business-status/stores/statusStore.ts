import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statusService } from '../services/statusService'
import type { BusinessStatus, BusinessStatusUpdate, BusinessStatusResponse } from '../types'

export const useStatusStore = defineStore('status', () => {
  // State
  const currentStatus = ref<BusinessStatusResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const status = computed(() => currentStatus.value?.status || 'available')
  const waitMinutes = computed(() => currentStatus.value?.estimated_wait_minutes || 0)
  const lastUpdated = computed(() => currentStatus.value?.updated_at || null)

  // Actions
  async function fetchCurrentStatus(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const data = await statusService.getCurrentStatus()
      currentStatus.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch status'
      console.error('[StatusStore] fetchCurrentStatus error:', err)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(data: BusinessStatusUpdate): Promise<{ success: boolean; error?: string }> {
    loading.value = true
    error.value = null

    try {
      const response = await statusService.updateStatus(data)
      currentStatus.value = response
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update status'
      error.value = errorMessage
      console.error('[StatusStore] updateStatus error:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  function resetError(): void {
    error.value = null
  }

  return {
    // State
    currentStatus,
    loading,
    error,

    // Getters
    status,
    waitMinutes,
    lastUpdated,

    // Actions
    fetchCurrentStatus,
    updateStatus,
    resetError,
  }
})
