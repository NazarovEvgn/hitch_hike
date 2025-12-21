export type BusinessType = 'car_wash' | 'auto_repair' | 'tire_service' | 'beauty_salon'

export interface Business {
  id: number
  name: string
  business_type: BusinessType
  address: string
  phones: string[]
  email: string
  description?: string
  logo_url?: string
  latitude: number
  longitude: number
  created_at: string
  updated_at: string
}

export interface BusinessUpdateInput {
  name: string
  business_type: BusinessType
  address: string
  phones: string[]
  description?: string
  logo_url?: string
}
