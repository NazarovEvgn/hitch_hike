import { apiClient } from '@/core/api/client'
import type { Service, ServiceCreateInput, ServiceUpdateInput } from '../types'

export const servicesApiService = {
  /**
   * Get all services for current business
   */
  async getAll(): Promise<Service[]> {
    const response = await apiClient.get<Service[]>('/admin/services')
    return response.data
  },

  /**
   * Create new service
   */
  async create(data: ServiceCreateInput): Promise<Service> {
    const response = await apiClient.post<Service>('/admin/services', data)
    return response.data
  },

  /**
   * Update existing service
   */
  async update(id: number, data: ServiceUpdateInput): Promise<Service> {
    const response = await apiClient.patch<Service>(`/admin/services/${id}`, data)
    return response.data
  },

  /**
   * Delete service
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/admin/services/${id}`)
  },
}
