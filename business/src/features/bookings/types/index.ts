export type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled'

export interface Booking {
  id: number
  business_id: number
  user_id: number | null
  employee_id: number | null
  service_id: number | null
  booking_date: string
  booking_time: string
  status: BookingStatus
  client_name: string
  client_phone: string
  notes: string | null
  came_through_app: boolean
  created_at: string
  updated_at: string
  service?: {
    id: number
    name: string
  }
  employee?: {
    id: number
    name: string
  }
}

export interface BookingStatusUpdate {
  status: BookingStatus
}

export interface BookingCreateInput {
  service_id: number
  employee_id?: number | null
  booking_date: string
  booking_time: string
  client_name: string
  client_phone: string
  notes?: string
}

export interface BookingFilters {
  status?: BookingStatus | null
  employee_id?: number | null
}

export interface StatusOption {
  value: BookingStatus | null
  label: string
  color: string
}
