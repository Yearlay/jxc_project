import request from '../utils/request'

export const getVehicleList = (keyword = '') =>
  request.get('/api/vehicle/list', { params: keyword ? { keyword } : {} })

export const addVehicle = (data) => request.post('/api/vehicle/add', data)

export const updateVehicle = (data) => request.put('/api/vehicle/update', data)

export const deleteVehicle = (data) => request.delete('/api/vehicle/delete', { data })
