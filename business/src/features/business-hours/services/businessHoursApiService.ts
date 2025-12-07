import { apiClient } from '@/core/api/client'
import type { BusinessHour, BusinessHoursUpdateInput } from '../types'

export const businessHoursApiService = {
  /**
   * Get business hours for all days
   */
  async getBusinessHours(): Promise<BusinessHour[]> {
    const response = await apiClient.get<BusinessHour[]>('/admin/business-hours')
    return response.data
  },

  /**
   * Update business hours for all days
   */
  async updateBusinessHours(data: BusinessHoursUpdateInput): Promise<BusinessHour[]> {
    const response = await apiClient.put<BusinessHour[]>('/admin/business-hours', data)
    return response.data
  },
}
