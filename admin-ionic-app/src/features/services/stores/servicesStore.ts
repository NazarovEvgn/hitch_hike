import { defineStore } from 'pinia'
import { ref } from 'vue'
import { servicesApiService } from '../services/servicesApiService'
import type { Service, ServiceCreateInput, ServiceUpdateInput } from '../types'

export const useServicesStore = defineStore('services', () => {
  // State
  const services = ref<Service[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchServices(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const data = await servicesApiService.getAll()
      services.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch services'
      console.error('[ServicesStore] fetchServices error:', err)
    } finally {
      loading.value = false
    }
  }

  async function createService(
    data: ServiceCreateInput
  ): Promise<{ success: boolean; error?: string }> {
    loading.value = true
    error.value = null

    try {
      const newService = await servicesApiService.create(data)
      services.value.push(newService)
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create service'
      error.value = errorMessage
      console.error('[ServicesStore] createService error:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function updateService(
    id: number,
    data: ServiceUpdateInput
  ): Promise<{ success: boolean; error?: string }> {
    loading.value = true
    error.value = null

    try {
      const updatedService = await servicesApiService.update(id, data)
      const index = services.value.findIndex((s) => s.id === id)
      if (index !== -1) {
        services.value[index] = updatedService
      }
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update service'
      error.value = errorMessage
      console.error('[ServicesStore] updateService error:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function deleteService(id: number): Promise<{ success: boolean; error?: string }> {
    loading.value = true
    error.value = null

    try {
      await servicesApiService.delete(id)
      services.value = services.value.filter((s) => s.id !== id)
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete service'
      error.value = errorMessage
      console.error('[ServicesStore] deleteService error:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function toggleServiceActive(id: number): Promise<{ success: boolean; error?: string }> {
    const service = services.value.find((s) => s.id === id)
    if (!service) {
      return { success: false, error: 'Service not found' }
    }

    return await updateService(id, { is_active: !service.is_active })
  }

  function resetError(): void {
    error.value = null
  }

  return {
    // State
    services,
    loading,
    error,

    // Actions
    fetchServices,
    createService,
    updateService,
    deleteService,
    toggleServiceActive,
    resetError,
  }
})
