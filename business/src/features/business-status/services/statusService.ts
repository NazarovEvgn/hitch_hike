import { apiClient } from '@/core/api/client'
import type { BusinessStatusUpdate, BusinessStatusResponse } from '../types'

export const statusService = {
  /**
   * Get current business status
   */
  async getCurrentStatus(): Promise<BusinessStatusResponse> {
    const response = await apiClient.get<BusinessStatusResponse>('/admin/status/current')
    return response.data
  },

  /**
   * Update business status
   */
  async updateStatus(data: BusinessStatusUpdate): Promise<BusinessStatusResponse> {
    const response = await apiClient.patch<BusinessStatusResponse>('/admin/status', data)
    return response.data
  },
}
