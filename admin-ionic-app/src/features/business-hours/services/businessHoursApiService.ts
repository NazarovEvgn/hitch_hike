import axios from 'axios'
import type { BusinessHour, BusinessHoursUpdateInput } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const businessHoursApiService = {
  /**
   * Get business hours for all days
   */
  async getBusinessHours(): Promise<BusinessHour[]> {
    const response = await axios.get<BusinessHour[]>(`${API_BASE_URL}/admin/business-hours`)
    return response.data
  },

  /**
   * Update business hours for all days
   */
  async updateBusinessHours(data: BusinessHoursUpdateInput): Promise<BusinessHour[]> {
    const response = await axios.put<BusinessHour[]>(`${API_BASE_URL}/admin/business-hours`, data)
    return response.data
  },
}
