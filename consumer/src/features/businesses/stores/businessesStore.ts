import { defineStore } from 'pinia'
import { ref } from 'vue'
import { businessesApiService } from '../services/businessesApiService'
import type { Business, BusinessType, NearbyBusinessesParams } from '../types'

export const useBusinessesStore = defineStore('businesses', () => {
  const businesses = ref<Business[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchNearby(params: NearbyBusinessesParams): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const data = await businessesApiService.getNearby(params)
      businesses.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch businesses'
      console.error('[BusinessesStore] fetchNearby error:', err)
    } finally {
      loading.value = false
    }
  }

  function filterByType(type: BusinessType | null): Business[] {
    if (!type) return businesses.value
    return businesses.value.filter(b => b.business_type === type)
  }

  return {
    businesses,
    loading,
    error,
    fetchNearby,
    filterByType,
  }
})
