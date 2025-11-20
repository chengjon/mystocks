import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import cacheManager from '@/utils/cache'

import dashboardApi from './dashboard'
// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 导入行业概念分析API
import industryConceptApi from './industryConcept'

// 请求拦截器 - 已移除认证头
// request.interceptors.request.use(
//   config => {
//     const token = localStorage.getItem('token')
//     if (token) {
//       config.headers['Authorization'] = `Bearer ${token}`
//     }
//     return config
//   },
//   error => {
//     console.error('Request error:', error)
//     return Promise.reject(error)
//   }
// )

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // ElMessage.error('未授权,请重新登录')
          // localStorage.removeItem('token')
          // localStorage.removeItem('user')
          // router.push('/login')
          ElMessage.error('未授权,但已禁用登录要求')
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(error.response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

// 认证 API - 已禁用认证功能
export const authApi = {
  login(username, password) {
    // 已禁用登录功能
    return Promise.resolve({
      success: false,
      message: '登录功能已禁用'
    })
  },
  logout() {
    // 已禁用登出功能
    return Promise.resolve({
      success: true,
      message: '登出功能已禁用'
    })
  },
  getCurrentUser() {
    // 已禁用获取用户信息
    return Promise.resolve({
      success: false,
      message: '用户信息获取已禁用'
    })
  },
  refreshToken() {
    // 已禁用令牌刷新
    return Promise.resolve({
      success: false,
      message: '令牌刷新已禁用'
    })
  }
}

// 数据 API
export const dataApi = {
  async getStocksBasic(params) {
    return cacheManager.withCache(
      () => request.get('/data/stocks/basic', { params }),
      'stocks_basic',
      params,
      300000 // 5分钟缓存
    )
  },
  
  async getStocksIndustries() {
    return cacheManager.withCache(
      () => request.get('/data/stocks/industries'),
      'stocks_industries',
      {},
      3600000 // 1小时缓存
    )
  },
  
  async getStocksConcepts() {
    return cacheManager.withCache(
      () => request.get('/data/stocks/concepts'),
      'stocks_concepts',
      {},
      3600000 // 1小时缓存
    )
  },
  async getDailyKline(params) {
    return cacheManager.withCache(
      () => request.get('/data/stocks/daily', { params }),
      'daily_kline',
      params,
      300000 // 5分钟缓存
    )
  },
  
  async getMarketOverview() {
    return cacheManager.withCache(
      () => request.get('/data/markets/overview'),
      'market_overview',
      {},
      600000 // 10分钟缓存
    )
  },
  
  async searchStocks(keyword) {
    return cacheManager.withCache(
      () => request.get('/data/stocks/search', { params: { keyword } }),
      'search_stocks',
      { keyword },
      180000 // 3分钟缓存
    )
  },
  
  async getKline(params) {
    // 使用不需要认证的market/kline端点
    return cacheManager.withCache(
      () => request.get('/market/kline', { 
        params: {
          ...params,
          stock_code: params.symbol, // 将symbol转换为stock_code参数
          period: params.period || 'daily', // 使用daily作为默认周期
          adjust: 'qfq' // 默认使用前复权
        }
      }),
      'kline',
      params,
      300000 // 5分钟缓存
    )
  },

  // 股票详情相关API
  async getStockDetail(symbol) {
    return cacheManager.withCache(
      () => request.get(`/data/stocks/${symbol}/detail`),
      'stock_detail',
      { symbol },
      900000 // 15分钟缓存
    )
  },

  async getStockIntraday(symbol, date) {
    return cacheManager.withCache(
      () => request.get('/data/stocks/intraday', { 
        params: { symbol, date } 
      }),
      'stock_intraday',
      { symbol, date },
      900000 // 15分钟缓存
    )
  },

  async getTradingSummary(symbol, period) {
    return cacheManager.withCache(
      () => request.get(`/data/stocks/${symbol}/trading-summary`, {
        params: { period }
      }),
      'trading_summary',
      { symbol, period },
      3600000 // 1小时缓存
    )
  }
}

// 监控 API
export const monitoringApi = {
  async getHealthStatus() {
    return request.get('/health')
  },
  
  async getDetailedHealthCheck() {
    return request.get('/health/detailed')
  },
  
  async getSystemHealth() {
    return request.get('/api/health')
  },
  
  async getDetailedSystemHealth() {
    return request.get('/api/health/detailed')
  }
}

export default request
