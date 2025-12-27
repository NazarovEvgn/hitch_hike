export type Gender = 'male' | 'female' | 'other'

export interface UserProfile {
  id: number
  email: string | null
  phone: string | null
  name: string
  gender: Gender | null
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface ProfileUpdateData {
  name?: string
  gender?: Gender | null
  email?: string | null
}
