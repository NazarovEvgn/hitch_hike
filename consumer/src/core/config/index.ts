export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export default {
  apiBaseUrl: API_BASE_URL,
  dgisApiKey: import.meta.env.VITE_DGIS_API_KEY || '',
}
