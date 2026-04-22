import request from '../utils/request'

export const getPurchaseStaffList = (keyword = '') =>
  request.get('/api/purchase-staff/list', { params: keyword ? { keyword } : {} })

export const addPurchaseStaff = (data) => request.post('/api/purchase-staff/add', data)

export const updatePurchaseStaff = (data) => request.put('/api/purchase-staff/update', data)

export const deletePurchaseStaff = (data) => request.delete('/api/purchase-staff/delete', { data })
