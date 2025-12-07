export interface Service {
  id: number
  business_id: number
  name: string
  description: string | null
  price: number
  duration_minutes: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ServiceCreateInput {
  name: string
  description?: string
  price: number
  duration_minutes: number
  is_active: boolean
}

export interface ServiceUpdateInput {
  name?: string
  description?: string
  price?: number
  duration_minutes?: number
  is_active?: boolean
}

export interface ServiceFormData {
  name: string
  description: string
  price: number
  duration_minutes: number
  is_active: boolean
}
