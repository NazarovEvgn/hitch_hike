import { apiClient } from '@/core/api/client'
import type { Employee, EmployeeCreateInput, EmployeeUpdateInput } from '../types'

export const employeesApiService = {
  /**
   * Get all employees for current business
   */
  async getEmployees(): Promise<Employee[]> {
    const response = await apiClient.get<Employee[]>('/admin/employees')
    return response.data
  },

  /**
   * Create a new employee
   */
  async createEmployee(data: EmployeeCreateInput): Promise<Employee> {
    const response = await apiClient.post<Employee>('/admin/employees', data)
    return response.data
  },

  /**
   * Update an employee
   */
  async updateEmployee(id: number, data: EmployeeUpdateInput): Promise<Employee> {
    const response = await apiClient.patch<Employee>(`/admin/employees/${id}`, data)
    return response.data
  },

  /**
   * Delete an employee
   */
  async deleteEmployee(id: number): Promise<void> {
    await apiClient.delete(`/admin/employees/${id}`)
  },

  /**
   * Toggle employee active status
   */
  async toggleEmployeeActive(id: number): Promise<Employee> {
    const response = await apiClient.patch<Employee>(`/admin/employees/${id}/toggle-active`)
    return response.data
  },
}
