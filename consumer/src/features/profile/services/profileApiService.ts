import { apiClient } from '@/core/api/client'
import type { UserProfile, ProfileUpdateData } from '../types'

export const profileApiService = {
  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/profile/me')
    return response.data
  },

  /**
   * Update current user profile
   */
  async updateProfile(data: ProfileUpdateData): Promise<UserProfile> {
    const response = await apiClient.patch<UserProfile>('/profile/me', data)
    return response.data
  },

  /**
   * Upload user avatar
   */
  async uploadAvatar(file: File): Promise<UserProfile> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<UserProfile>('/profile/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Delete user avatar
   */
  async deleteAvatar(): Promise<UserProfile> {
    const response = await apiClient.delete<UserProfile>('/profile/me/avatar')
    return response.data
  },
}
