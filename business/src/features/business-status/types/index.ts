export type BusinessStatus = 'available' | 'busy' | 'very_busy'

export interface BusinessStatusUpdate {
  status: BusinessStatus
  estimated_wait_minutes: number
}

export interface BusinessStatusResponse {
  id: number
  business_id: number
  status: BusinessStatus
  estimated_wait_minutes: number
  updated_at: string
}

export interface StatusOption {
  value: BusinessStatus
  label: string
  emoji: string
  description: string
  color: string
}
