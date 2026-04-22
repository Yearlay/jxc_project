import request from '../utils/request'

export const getMemberTypeList = (name = '') =>
  request.get('/api/member-type/list', { params: name ? { name } : {} })

export const addMemberType = (data) => request.post('/api/member-type/add', data)

export const updateMemberType = (data) => request.put('/api/member-type/update', data)

export const deleteMemberType = (data) => request.delete('/api/member-type/delete', { data })
