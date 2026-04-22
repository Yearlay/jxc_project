import request from '../utils/request'

export const getTerminalList = (keyword = '') =>
  request.get('/api/terminal/list', { params: keyword ? { keyword } : {} })

export const addTerminal = (data) => request.post('/api/terminal/add', data)

export const updateTerminal = (data) => request.put('/api/terminal/update', data)

export const deleteTerminal = (data) => request.delete('/api/terminal/delete', { data })
