import request from '../utils/request'

export const getPaymentList = (name = '') =>
  request.get('/api/payment/list', { params: name ? { name } : {} })

export const addPayment = (data) => request.post('/api/payment/add', data)

export const updatePayment = (data) => request.put('/api/payment/update', data)

export const deletePayment = (data) => request.delete('/api/payment/delete', { data })
