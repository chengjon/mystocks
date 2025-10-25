import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - Week 3: 用户友好错误处理
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 优先使用后端返回的用户友好错误消息
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)

      // 特殊处理: 认证错误需要跳转到登录页
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
      }
    } else if (error.response) {
      // 如果后端没有返回友好消息，使用默认消息
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          // 尝试从响应中提取错误信息
          const errorMsg = error.response.data?.message ||
                          error.response.data?.detail ||
                          '请求失败，请稍后重试'
          ElMessage.error(errorMsg)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      ElMessage.error('网络错误，请检查连接后重试')
    } else {
      // 请求配置出错
      ElMessage.error('请求错误: ' + (error.message || '未知错误'))
    }

    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  login(username, password) {
    // 使用 URLSearchParams 来发送 form-data 格式,符合 OAuth2 标准
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    return request.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },
  logout() {
    return request.post('/auth/logout')
  },
  getCurrentUser() {
    return request.get('/auth/me')
  },
  refreshToken() {
    return request.post('/auth/refresh')
  }
}

// 数据 API
export const dataApi = {
  getStocksBasic(params) {
    return request.get('/data/stocks/basic', { params })
  },
  getDailyKline(params) {
    return request.get('/data/stocks/daily', { params })
  },
  getMarketOverview() {
    return request.get('/data/markets/overview')
  },
  searchStocks(keyword) {
    return request.get('/data/stocks/search', { params: { keyword } })
  }
}

export default request
