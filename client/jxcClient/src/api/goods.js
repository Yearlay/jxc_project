import request from '../utils/request'

export const getGoodsList = (params = {}) =>
  request.get('/api/goods/list', { params })

export const getNextGoodsCode = () => request.get('/api/goods/next-code')

export const addGoods = (data) => request.post('/api/goods/add', data)

export const updateGoods = (data) => request.put('/api/goods/update', data)

export const deleteGoods = (data) => request.delete('/api/goods/delete', { data })

export const getGoodsStockList = (goodsId) =>
  request.get('/api/goods/stock/list', { params: { goods_id: goodsId } })

export const addGoodsStock = (data) => request.post('/api/goods/stock/add', data)

export const updateGoodsStock = (data) => request.put('/api/goods/stock/update', data)

export const deleteGoodsStock = (data) => request.delete('/api/goods/stock/delete', { data })

export const transferGoodsStock = (data) => request.post('/api/goods/stock/transfer', data)