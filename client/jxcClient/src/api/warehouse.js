import request from '../utils/request'

export const getWarehouseList = (name = '') =>
  request.get('/api/warehouse/list', { params: name ? { name } : {} })

export const addWarehouse = (data) => request.post('/api/warehouse/add', data)

export const updateWarehouse = (data) => request.put('/api/warehouse/update', data)

export const deleteWarehouse = (data) => request.delete('/api/warehouse/delete', { data })
