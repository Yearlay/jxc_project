import request from '../utils/request'

// 原接口：权限组添加成员用
export const getUserList = () => request.get('/api/user/list')

// 用户管理接口
export const getManageUserList = (keyword = '') =>
  request.get('/api/user/manage/list', { params: keyword ? { keyword } : {} })

export const addManageUser = (data) => request.post('/api/user/manage/add', data)

export const updateManageUser = (data) => request.put('/api/user/manage/update', data)

export const resetPassword = (data) => request.put('/api/user/manage/reset-password', data)

export const deleteManageUser = (data) => request.delete('/api/user/manage/delete', { data })

