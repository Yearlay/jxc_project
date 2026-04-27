import request from '../utils/request'

export const getPosBootstrap = () => request.get('/api/pos/bootstrap')

export const searchPosGoods = (params) =>
  request.get('/api/pos/goods/search', { params })

export const savePosHold = (data) => request.post('/api/pos/hold', data)

export const getPosHoldList = () => request.get('/api/pos/hold/list')

export const takePosHold = (data) => request.post('/api/pos/hold/take', data)

export const deletePosHold = (data) =>
  request.delete('/api/pos/hold/delete', { data })

export const checkoutPosOrder = (data) => request.post('/api/pos/checkout', data)