import request from '../utils/request'

export const getManufacturerList = (keyword = '') =>
  request.get('/api/manufacturer/list', { params: keyword ? { keyword } : {} })

export const addManufacturer = (data) => request.post('/api/manufacturer/add', data)

export const updateManufacturer = (data) => request.put('/api/manufacturer/update', data)

export const deleteManufacturer = (data) => request.delete('/api/manufacturer/delete', { data })
