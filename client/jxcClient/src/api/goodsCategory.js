import request from '../utils/request'

export const getGoodsCategoryTree = () => request.get('/api/goods-category/tree')

export const addGoodsCategory = (data) => request.post('/api/goods-category/add', data)

export const updateGoodsCategory = (data) => request.put('/api/goods-category/update', data)

export const deleteGoodsCategory = (data) => request.delete('/api/goods-category/delete', { data })