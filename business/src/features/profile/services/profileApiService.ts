import { apiClient } from '@/core/api/client'
import type { Business, BusinessUpdateInput } from '../types'

export const profileApiService = {
  /**
   * Get current business profile
   */
  async getProfile(): Promise<Business> {
    const response = await apiClient.get<Business>('/admin/business/profile')
    return response.data
  },

  /**
   * Update business profile
   */
  async updateProfile(data: BusinessUpdateInput): Promise<Business> {
    const response = await apiClient.put<Business>('/admin/business/profile', data)
    return response.data
  },
}
