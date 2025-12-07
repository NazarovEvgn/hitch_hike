export interface BusinessHour {
  id?: number
  day_of_week: number // 0 = Monday, 6 = Sunday
  open_time: string | null // HH:MM:SS format
  close_time: string | null // HH:MM:SS format
  is_closed: boolean
}

export interface DaySchedule {
  name: string
  dayOfWeek: number
  isOpen: boolean
  openTime: string // HH:MM format for UI
  closeTime: string // HH:MM format for UI
  error: string | null
}

export interface BusinessHoursUpdateInput {
  hours: Array<{
    day_of_week: number
    is_closed: boolean
    open_time: string | null // HH:MM:SS format
    close_time: string | null // HH:MM:SS format
  }>
}
