import request from '../utils/request'

export const getCustomerList = (params) =>
  request.get('/api/customer/list', { params })

export const addCustomer = (data) => request.post('/api/customer/add', data)

export const updateCustomer = (data) => request.put('/api/customer/update', data)

export const rechargeCustomer = (data) => request.put('/api/customer/recharge', data)

export const deleteCustomer = (data) => request.delete('/api/customer/delete', { data })
