/**
 * Конфигурация приложения
 */

export const config = {
  apiBaseUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',

  // Время жизни токенов (в минутах)
  tokenExpiration: {
    access: 30,
    refresh: 7 * 24 * 60, // 7 дней
  },

  // Настройки localStorage
  storage: {
    accessTokenKey: 'accessToken',
    refreshTokenKey: 'refreshToken',
  },

  // Брендовые цвета
  theme: {
    primary: '#27126A', // Фиолетовый
    accent: '#98EA14',  // Зеленый
  },
} as const

export default config
