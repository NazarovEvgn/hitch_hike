import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BookingState, Booking, AvailableSlot } from '../types'
import { bookingApiService } from '../services/bookingApiService'
import { useAuthStore } from '@/features/auth/stores/authStore'

export const useBookingStore = defineStore('booking', () => {
  // Booking state
  const selectedBusinessId = ref<number | null>(null)
  const selectedServiceId = ref<number | null>(null)
  const selectedEmployeeId = ref<number | null>(null)
  const selectedDate = ref<string | null>(null)
  const selectedTime = ref<string | null>(null)

  // Available slots
  const availableSlots = ref<AvailableSlot[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Reset booking state
  function resetBooking() {
    selectedBusinessId.value = null
    selectedServiceId.value = null
    selectedEmployeeId.value = null
    selectedDate.value = null
    selectedTime.value = null
    availableSlots.value = []
    error.value = null
  }

  // Start new booking
  function startBooking(businessId: number) {
    resetBooking()
    selectedBusinessId.value = businessId
  }

  // Select service
  function selectService(serviceId: number) {
    selectedServiceId.value = serviceId
    // Reset subsequent selections
    selectedEmployeeId.value = null
    selectedDate.value = null
    selectedTime.value = null
  }

  // Select employee
  function selectEmployee(employeeId: number) {
    selectedEmployeeId.value = employeeId
    // Reset subsequent selections
    selectedDate.value = null
    selectedTime.value = null
  }

  // Select date
  function selectDate(date: string) {
    selectedDate.value = date
    selectedTime.value = null
  }

  // Select time
  function selectTime(time: string) {
    selectedTime.value = time
  }

  // Get available slots for employee on specific date
  async function fetchAvailableSlots(employeeId: number, date: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // Temporary mock data
      const mockSlots: AvailableSlot[] = []
      const times = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00']

      times.forEach(time => {
        mockSlots.push({
          date,
          time,
          employee_id: employeeId,
          service_id: selectedServiceId.value!,
        })
      })

      availableSlots.value = mockSlots
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch available slots'
      console.error('[BookingStore] fetchAvailableSlots error:', err)
    } finally {
      loading.value = false
    }
  }

  // Submit booking
  async function submitBooking(): Promise<boolean> {
    if (!selectedBusinessId.value || !selectedServiceId.value || !selectedEmployeeId.value || !selectedDate.value || !selectedTime.value) {
      error.value = 'Incomplete booking information'
      return false
    }

    loading.value = true
    error.value = null

    try {
      const authStore = useAuthStore()

      // Get client info from auth store
      const clientName = authStore.user?.name || 'Клиент'
      const clientPhone = authStore.user?.phone || ''

      const bookingData = {
        business_id: selectedBusinessId.value,
        service_id: selectedServiceId.value,
        employee_id: selectedEmployeeId.value,
        booking_date: selectedDate.value,
        booking_time: selectedTime.value,
        client_name: clientName,
        client_phone: clientPhone,
      }

      console.log('[BookingStore] Submitting booking:', bookingData)

      const booking = await bookingApiService.createBooking(bookingData)

      console.log('[BookingStore] Booking created:', booking)

      // Reset booking state after successful creation
      resetBooking()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create booking'
      console.error('[BookingStore] submitBooking error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    selectedBusinessId,
    selectedServiceId,
    selectedEmployeeId,
    selectedDate,
    selectedTime,
    availableSlots,
    loading,
    error,
    resetBooking,
    startBooking,
    selectService,
    selectEmployee,
    selectDate,
    selectTime,
    fetchAvailableSlots,
    submitBooking,
  }
})
