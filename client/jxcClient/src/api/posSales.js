import request from '../utils/request'

export const getPosSalesList = (params) =>
  request.get('/api/pos-sales/list', { params })

export const getPosSalesDetail = (id) =>
  request.get('/api/pos-sales/detail', { params: { id } })