import { apiClient } from '@/core/api/client'
import type { Booking, BookingStatusUpdate, BookingFilters } from '../types'

export const bookingsApiService = {
  async getAll(filters?: BookingFilters): Promise<Booking[]> {
    const params: any = {}
    if (filters?.status) params.status = filters.status
    if (filters?.employee_id) params.employee_id = filters.employee_id

    const response = await apiClient.get<Booking[]>('/admin/bookings', { params })
    return response.data
  },

  async updateStatus(id: number, data: BookingStatusUpdate): Promise<Booking> {
    const response = await apiClient.patch<Booking>(`/admin/bookings/${id}`, data)
    return response.data
  },
}
