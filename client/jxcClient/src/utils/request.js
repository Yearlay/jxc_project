import axios from 'axios'
import router from '../router'

const request = axios.create({
  baseURL: '',
  timeout: 10000,
})

// 请求拦截：自动注入 token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 自动跳转登录页
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      router.replace('/login')
    }
    return Promise.reject(error)
  }
)

export default request
