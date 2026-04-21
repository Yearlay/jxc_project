import request from '../utils/request'

export const getUserList = () => request.get('/api/user/list')
