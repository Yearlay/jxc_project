import request from '../utils/request'

export const getAreaList = (name = '') =>
  request.get('/api/area/list', { params: name ? { name } : {} })

export const addArea = (data) => request.post('/api/area/add', data)

export const updateArea = (data) => request.put('/api/area/update', data)

export const deleteArea = (data) => request.delete('/api/area/delete', { data })
