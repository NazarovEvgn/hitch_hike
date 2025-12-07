import { defineStore } from 'pinia'
import { ref } from 'vue'
import { businessHoursApiService } from '../services/businessHoursApiService'
import type { BusinessHour, BusinessHoursUpdateInput, DaySchedule } from '../types'

const DAY_NAMES = [
  'Понедельник',
  'Вторник',
  'Среда',
  'Четверг',
  'Пятница',
  'Суббота',
  'Воскресенье',
]

export const useBusinessHoursStore = defineStore('businessHours', () => {
  const businessHours = ref<BusinessHour[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Convert BusinessHour[] from API to DaySchedule[] for UI
   */
  function mapToSchedules(hours: BusinessHour[]): DaySchedule[] {
    const schedules: DaySchedule[] = []

    for (let i = 0; i < 7; i++) {
      const hour = hours.find(h => h.day_of_week === i)

      schedules.push({
        name: DAY_NAMES[i],
        dayOfWeek: i,
        isOpen: hour ? !hour.is_closed : false,
        openTime: hour?.open_time ? hour.open_time.substring(0, 5) : '09:00',
        closeTime: hour?.close_time ? hour.close_time.substring(0, 5) : '18:00',
        error: null,
      })
    }

    return schedules
  }

  /**
   * Convert DaySchedule[] from UI to BusinessHoursUpdateInput for API
   */
  function mapToApiFormat(schedules: DaySchedule[]): BusinessHoursUpdateInput {
    return {
      hours: schedules.map(schedule => ({
        day_of_week: schedule.dayOfWeek,
        is_closed: !schedule.isOpen,
        open_time: schedule.isOpen ? `${schedule.openTime}:00` : null,
        close_time: schedule.isOpen ? `${schedule.closeTime}:00` : null,
      })),
    }
  }

  async function fetchBusinessHours(): Promise<DaySchedule[]> {
    loading.value = true
    error.value = null

    try {
      const data = await businessHoursApiService.getBusinessHours()
      businessHours.value = data
      return mapToSchedules(data)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch business hours'
      console.error('[BusinessHoursStore] fetchBusinessHours error:', err)
      // Return default schedule on error
      return mapToSchedules([])
    } finally {
      loading.value = false
    }
  }

  async function updateBusinessHours(
    schedules: DaySchedule[]
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const input = mapToApiFormat(schedules)
      const updated = await businessHoursApiService.updateBusinessHours(input)
      businessHours.value = updated
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update business hours'
      console.error('[BusinessHoursStore] updateBusinessHours error:', err)
      return { success: false, error: errorMessage }
    }
  }

  return {
    businessHours,
    loading,
    error,
    fetchBusinessHours,
    updateBusinessHours,
  }
})
