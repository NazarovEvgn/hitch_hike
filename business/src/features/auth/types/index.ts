/**
 * Типы для auth feature
 */

// Данные для входа
export interface LoginCredentials {
  email: string
  password: string
}

// Данные для регистрации бизнеса
export interface BusinessRegistrationData {
  email: string
  password: string
  business_name: string
  business_type: string
  address: string
  phone: string
  latitude?: number
  longitude?: number
}

// Ответ от API при успешной аутентификации
export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Профиль бизнеса
export interface BusinessProfile {
  id: number
  name: string
  business_type: string
  address: string
  phone: string
  latitude: number | null
  longitude: number | null
  description: string | null
  created_at: string
  updated_at: string
}

// Пользователь (admin)
export interface User {
  id: number
  email: string
  user_type: 'business_admin'
  business_id: number
  created_at: string
}

// Результат операции (login/register)
export interface AuthResult {
  success: boolean
  error?: string
}
