import request from '../utils/request'

export const getUnitList = (name = '') =>
  request.get('/api/unit/list', { params: name ? { name } : {} })

export const addUnit = (data) => request.post('/api/unit/add', data)

export const updateUnit = (data) => request.put('/api/unit/update', data)

export const deleteUnit = (data) => request.delete('/api/unit/delete', { data })
