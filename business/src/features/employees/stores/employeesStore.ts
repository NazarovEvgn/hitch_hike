import { defineStore } from 'pinia'
import { ref } from 'vue'
import { employeesApiService } from '../services/employeesApiService'
import type { Employee, EmployeeFormData } from '../types'

export const useEmployeesStore = defineStore('employees', () => {
  const employees = ref<Employee[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchEmployees() {
    loading.value = true
    error.value = null

    try {
      employees.value = await employeesApiService.getEmployees()
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка загрузки мастеров'
      error.value = errorMessage
      console.error('[EmployeesStore] Failed to fetch employees:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function createEmployee(data: EmployeeFormData) {
    loading.value = true
    error.value = null

    try {
      const newEmployee = await employeesApiService.createEmployee({
        name: data.name,
        phone: data.phone,
        photo_url: data.photo_url || null,
        service_ids: data.service_ids,
      })

      employees.value.push(newEmployee)
      return { success: true, data: newEmployee }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка создания мастера'
      error.value = errorMessage
      console.error('[EmployeesStore] Failed to create employee:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function updateEmployee(id: number, data: EmployeeFormData) {
    loading.value = true
    error.value = null

    try {
      const updatedEmployee = await employeesApiService.updateEmployee(id, {
        name: data.name,
        phone: data.phone,
        photo_url: data.photo_url || null,
        is_active: data.is_active,
        service_ids: data.service_ids,
      })

      const index = employees.value.findIndex((e) => e.id === id)
      if (index !== -1) {
        employees.value[index] = updatedEmployee
      }

      return { success: true, data: updatedEmployee }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка обновления мастера'
      error.value = errorMessage
      console.error('[EmployeesStore] Failed to update employee:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function deleteEmployee(id: number) {
    loading.value = true
    error.value = null

    try {
      await employeesApiService.deleteEmployee(id)
      employees.value = employees.value.filter((e) => e.id !== id)
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка удаления мастера'
      error.value = errorMessage
      console.error('[EmployeesStore] Failed to delete employee:', err)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  async function toggleEmployeeActive(id: number) {
    try {
      const updatedEmployee = await employeesApiService.toggleEmployeeActive(id)

      const index = employees.value.findIndex((e) => e.id === id)
      if (index !== -1) {
        employees.value[index] = updatedEmployee
      }

      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка изменения статуса'
      error.value = errorMessage
      console.error('[EmployeesStore] Failed to toggle employee active:', err)
      return { success: false, error: errorMessage }
    }
  }

  return {
    employees,
    loading,
    error,
    fetchEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
    toggleEmployeeActive,
  }
})
