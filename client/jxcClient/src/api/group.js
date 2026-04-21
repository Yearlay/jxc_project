import request from '../utils/request'

export const getGroupList = () => request.get('/api/group/list')
export const addGroup = (data) => request.post('/api/group/add', data)
export const renameGroup = (data) => request.put('/api/group/rename', data)
export const deleteGroup = (data) => request.delete('/api/group/delete', { data })

export const getGroupMenus = (groupId) =>
  request.get('/api/group/menus', { params: { group_id: groupId } })
export const saveGroupMenus = (data) => request.post('/api/group/menus/save', data)

export const getGroupMembers = (groupId) =>
  request.get('/api/group/members', { params: { group_id: groupId } })
export const addGroupMember = (data) => request.post('/api/group/members/add', data)
export const removeGroupMember = (data) =>
  request.delete('/api/group/members/remove', { data })
