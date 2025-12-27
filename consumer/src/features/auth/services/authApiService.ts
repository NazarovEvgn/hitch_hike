import { apiClient } from '@/core/api/client'
import type {
  Token,
  PhoneOTPRequest,
  OTPVerifyRequest,
  BusinessLoginRequest,
  OTPResponse
} from '../types'

export const authApiService = {
  /**
   * DEV MODE: Direct login with phone number (no OTP verification)
   */
  async devLogin(data: PhoneOTPRequest): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/dev-login', data)
    return response.data
  },

  /**
   * Send OTP code to phone (passwordless login for clients)
   */
  async sendOTP(data: PhoneOTPRequest): Promise<OTPResponse> {
    const response = await apiClient.post<OTPResponse>('/auth/send-otp', data)
    return response.data
  },

  /**
   * Verify OTP code and login (passwordless login for clients)
   */
  async verifyOTP(data: OTPVerifyRequest): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/verify-otp', data)
    return response.data
  },

  /**
   * Login for business admins (email + password)
   */
  async loginBusiness(data: BusinessLoginRequest): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/login/business', data)
    return response.data
  },
}
