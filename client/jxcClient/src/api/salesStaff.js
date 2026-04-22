import request from '../utils/request'

export const getSalesStaffList = (keyword = '') =>
  request.get('/api/sales-staff/list', { params: keyword ? { keyword } : {} })

export const addSalesStaff = (data) => request.post('/api/sales-staff/add', data)

export const updateSalesStaff = (data) => request.put('/api/sales-staff/update', data)

export const deleteSalesStaff = (data) => request.delete('/api/sales-staff/delete', { data })
