export interface Employee {
  id: number
  business_id: number
  name: string
  phone: string
  photo_url: string | null
  is_active: boolean
  service_ids: number[]
  created_at: string
  updated_at: string
}

export interface EmployeeFormData {
  name: string
  phone: string
  photo_url?: string | null
  is_active: boolean
  service_ids: number[]
}

export interface EmployeeCreateInput {
  name: string
  phone: string
  photo_url?: string | null
  service_ids: number[]
}

export interface EmployeeUpdateInput {
  name?: string
  phone?: string
  photo_url?: string | null
  is_active?: boolean
  service_ids?: number[]
}
