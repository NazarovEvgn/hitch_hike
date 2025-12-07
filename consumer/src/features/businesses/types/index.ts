export type BusinessType = 'car_wash' | 'auto_repair' | 'tire_service' | 'beauty_salon'
export type BusinessStatus = 'available' | 'busy' | 'very_busy'

export interface BusinessStatusInfo {
  status: BusinessStatus
  estimated_wait_minutes: number
  updated_at: string
}

export interface Business {
  id: number
  name: string
  business_type: BusinessType
  address: string
  phone: string
  email: string
  description?: string
  logo_url?: string
  latitude: number
  longitude: number
  status?: BusinessStatusInfo
  created_at: string
  updated_at: string
}

export interface NearbyBusinessesParams {
  latitude: number
  longitude: number
  radius_km?: number
  business_type?: BusinessType
}
