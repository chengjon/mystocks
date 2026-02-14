import axios from 'axios'
// ElMessage auto-imported by unplugin-vue-components
import cacheManager from '@/utils/cache'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 从localStorage获取token
request.interceptors.request.use(
  config => {
    // 从localStorage获取token（登录后由auth.ts保存）
    const token = localStorage.getItem('auth_token')
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

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token过期或无效，清除session并跳转登录页
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('auth_token')
          localStorage.removeItem('auth_user')
          // 保存当前路径，登录后返回
          sessionStorage.setItem('redirectPath', window.location.pathname)
          router.push('/login')
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

// 认证 API (v1)
export const authApi = {
  login(username, password) {
    // 后端使用 OAuth2PasswordRequestForm，需要表单数据格式
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return request.post('/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },
  logout() {
    return request.post('/v1/auth/logout')
  },
  getCurrentUser() {
    return request.get('/v1/auth/me')
  },
  refreshToken() {
    return request.post('/v1/auth/refresh')
  }
}

// 数据 API (v1)
export const dataApi = {
  async getStocksBasic(params) {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/basic', { params }),
      'stocks_basic',
      params,
      300000 // 5分钟缓存
    )
  },

  async getStocksIndustries() {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/industries'),
      'stocks_industries',
      {},
      3600000 // 1小时缓存
    )
  },

  async getStocksConcepts() {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/concepts'),
      'stocks_concepts',
      {},
      3600000 // 1小时缓存
    )
  },
  async getDailyKline(params) {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/daily', { params }),
      'daily_kline',
      params,
      300000 // 5分钟缓存
    )
  },

  async getMarketOverview() {
    return cacheManager.withCache(
      () => request.get('/v1/data/markets/overview'),
      'market_overview',
      {},
      600000 // 10分钟缓存
    )
  },

  async searchStocks(keyword) {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/search', { params: { keyword } }),
      'search_stocks',
      { keyword },
      180000 // 3分钟缓存
    )
  },

  async getKline(params) {
    // 使用不需要认证的market/kline端点
    return cacheManager.withCache(
      () => request.get('/v1/market/kline', {
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
      () => request.get(`/v1/data/stocks/${symbol}/detail`),
      'stock_detail',
      { symbol },
      900000 // 15分钟缓存
    )
  },

  async getStockIntraday(symbol, date) {
    return cacheManager.withCache(
      () => request.get('/v1/data/stocks/intraday', {
        params: { symbol, date }
      }),
      'stock_intraday',
      { symbol, date },
      900000 // 15分钟缓存
    )
  },

  async getTradingSummary(symbol, period) {
    return cacheManager.withCache(
      () => request.get(`/v1/data/stocks/${symbol}/trading-summary`, {
        params: { period }
      }),
      'trading_summary',
      { symbol, period },
      3600000 // 1小时缓存
    )
  }
}

// 监控 API (v1)
export const monitoringApi = {
  // 健康检查 (root level)
  async getHealthStatus() {
    return request.get('/health')
  },
  async getDetailedHealthCheck() {
    return request.get('/health/detailed')
  },

  // 告警规则管理
  async getAlertRules() {
    return request.get('/v1/monitoring/alert-rules')
  },
  async createAlertRule(data) {
    return request.post('/v1/monitoring/alert-rules', data)
  },
  async updateAlertRule(ruleId, data) {
    return request.put(`/v1/monitoring/alert-rules/${ruleId}`, data)
  },
  async deleteAlertRule(ruleId) {
    return request.delete(`/v1/monitoring/alert-rules/${ruleId}`)
  },

  // 告警记录
  async getAlerts(params) {
    return request.get('/v1/monitoring/alerts', { params })
  },
  async markAlertRead(alertId) {
    return request.post(`/v1/monitoring/alerts/${alertId}/mark-read`)
  },
  async markAllAlertsRead() {
    return request.post('/v1/monitoring/alerts/mark-all-read')
  },

  // 实时监控数据
  async getRealtimeData(params) {
    return request.get('/v1/monitoring/realtime', { params })
  },
  async getRealtimeBySymbol(symbol) {
    return request.get(`/v1/monitoring/realtime/${symbol}`)
  },
  async refreshRealtimeData() {
    return request.post('/v1/monitoring/realtime/fetch')
  },

  // 龙虎榜数据
  async getDragonTiger(params) {
    return request.get('/v1/monitoring/dragon-tiger', { params })
  },
  async refreshDragonTiger() {
    return request.post('/v1/monitoring/dragon-tiger/fetch')
  },

  // 监控摘要和统计
  async getSummary() {
    return request.get('/v1/monitoring/summary')
  },
  async getTodayStats() {
    return request.get('/v1/monitoring/stats/today')
  },

  // 监控控制
  async startMonitoring() {
    return request.post('/v1/monitoring/control/start')
  },
  async stopMonitoring() {
    return request.post('/v1/monitoring/control/stop')
  },
  async getMonitoringStatus() {
    return request.get('/v1/monitoring/control/status')
  }
}

// 技术分析 API (v1)
export const technicalApi = {
  // 获取所有技术指标
  async getIndicators(symbol, params) {
    return request.get(`/v1/technical/${symbol}/indicators`, { params })
  },
  // 趋势指标 (MA/EMA/MACD/DMI/SAR)
  async getTrendIndicators(symbol, params) {
    return request.get(`/v1/technical/${symbol}/trend`, { params })
  },
  // 动量指标 (RSI/KDJ/CCI/WR/ROC)
  async getMomentumIndicators(symbol, params) {
    return request.get(`/v1/technical/${symbol}/momentum`, { params })
  },
  // 波动性指标 (BOLL/ATR/KC/STDDEV)
  async getVolatilityIndicators(symbol, params) {
    return request.get(`/v1/technical/${symbol}/volatility`, { params })
  },
  // 成交量指标 (OBV/VWAP/Volume MA)
  async getVolumeIndicators(symbol, params) {
    return request.get(`/v1/technical/${symbol}/volume`, { params })
  },
  // 交易信号
  async getSignals(symbol, params) {
    return request.get(`/v1/technical/${symbol}/signals`, { params })
  },
  // K线历史数据
  async getHistory(symbol, params) {
    return request.get(`/v1/technical/${symbol}/history`, { params })
  },
  // 批量获取技术指标
  async getBatchIndicators(symbols, params) {
    return request.post('/v1/technical/batch/indicators', { symbols, ...params })
  },
  // 技术形态检测
  async getPatterns(symbol) {
    return request.get(`/v1/technical/patterns/${symbol}`)
  },
  // 快捷方法 - 趋势分析
  async getTrend(symbol, params) {
    return this.getTrendIndicators(symbol, params)
  },
  // 快捷方法 - 动量分析
  async getMomentum(symbol, params) {
    return this.getMomentumIndicators(symbol, params)
  },
  // 快捷方法 - 波动性分析
  async getVolatility(symbol, params) {
    return this.getVolatilityIndicators(symbol, params)
  },
  // 快捷方法 - 成交量分析
  async getVolume(symbol, params) {
    return this.getVolumeIndicators(symbol, params)
  }
}

// 策略管理 API (v1)
export const strategyApi = {
  // 策略 CRUD
  async getStrategies(params) {
    return request.get('/v1/strategy/strategies', { params })
  },
  async createStrategy(data) {
    return request.post('/v1/strategy/strategies', data)
  },
  async getStrategy(strategyId) {
    return request.get(`/v1/strategy/strategies/${strategyId}`)
  },
  async updateStrategy(strategyId, data) {
    return request.put(`/v1/strategy/strategies/${strategyId}`, data)
  },
  async deleteStrategy(strategyId) {
    return request.delete(`/v1/strategy/strategies/${strategyId}`)
  },

  // 模型训练
  async trainModel(data) {
    return request.post('/v1/strategy/models/train', data)
  },
  async getTrainingStatus(taskId) {
    return request.get(`/v1/strategy/models/training/${taskId}/status`)
  },
  async getModels(params) {
    return request.get('/v1/strategy/models', { params })
  },

  // 回测
  async runBacktest(data) {
    return request.post('/v1/strategy/backtest/run', data)
  },
  async getBacktestResults(params) {
    return request.get('/v1/strategy/backtest/results', { params })
  },
  async getBacktestResult(backtestId) {
    return request.get(`/v1/strategy/backtest/results/${backtestId}`)
  },
  async getBacktestChartData(backtestId) {
    return request.get(`/v1/strategy/backtest/results/${backtestId}/chart-data`)
  },

  // InStock 策略系统
  async getDefinitions() {
    return request.get('/v1/strategy/definitions')
  },
  async runSingle(params) {
    return request.post('/v1/strategy/run/single', null, { params })
  },
  async runBatch(params) {
    return request.post('/v1/strategy/run/batch', null, { params })
  },
  async getResults(params) {
    return request.get('/v1/strategy/results', { params })
  },
  async getMatchedStocks(params) {
    return request.get('/v1/strategy/matched-stocks', { params })
  },
  async getStats(params) {
    return request.get('/v1/strategy/stats/summary', { params })
  }
}

// 市场数据 API (v1)
export const marketApi = {
  // 资金流向
  async getFundFlow(params) {
    return request.get('/v1/market/fund-flow', { params })
  },
  async refreshFundFlow() {
    return request.post('/v1/market/fund-flow/refresh')
  },

  // ETF数据
  async getETFList(params) {
    return request.get('/v1/market/etf/list', { params })
  },
  async refreshETF() {
    return request.post('/v1/market/etf/refresh')
  },

  // 竞价抢筹
  async getChipRace(params) {
    return request.get('/v1/market/chip-race', { params })
  },
  async refreshChipRace() {
    return request.post('/v1/market/chip-race/refresh')
  },

  // 龙虎榜
  async getLHB(params) {
    return request.get('/v1/market/lhb', { params })
  },
  async refreshLHB() {
    return request.post('/v1/market/lhb/refresh')
  },

  // 实时行情
  async getQuotes(symbols) {
    return request.get('/v1/market/quotes', { params: { symbols } })
  },

  // 股票列表
  async getStocks(params) {
    return request.get('/v1/market/stocks', { params })
  },

  // K线数据
  async getKline(params) {
    return request.get('/v1/market/kline', { params })
  },

  // 市场热力图
  async getHeatmap(params) {
    return request.get('/v1/market/heatmap', { params })
  }
}

// 风险管理 API (v1)
export const riskApi = {
  async getVarCvar(params) {
    return request.get('/v1/risk/var-cvar', { params })
  },
  async getBeta(params) {
    return request.get('/v1/risk/beta', { params })
  },
  async getDashboard() {
    return request.get('/v1/risk/dashboard')
  },
  async getMetricsHistory(params) {
    return request.get('/v1/risk/metrics/history', { params })
  },
  async getAlerts(params) {
    return request.get('/v1/risk/alerts', { params })
  },
  async createAlert(data) {
    return request.post('/v1/risk/alerts', data)
  }
}

// 自选股 API (v1)
export const watchlistApi = {
  async getWatchlist() {
    return request.get('/watchlist/')
  },
  // 简化版本 - 只需要股票代码
  async addStock(symbol) {
    return request.post('/watchlist/add', { symbol })
  },
  async removeStock(symbol) {
    return request.delete(`/watchlist/remove/${symbol}`)
  },
  async checkStock(symbol) {
    return request.get(`/watchlist/check/${symbol}`)
  },
  // 完整版本 - 支持所有参数（可选）
  async addToWatchlist(data) {
    return request.post('/watchlist/', data)
  },
  async removeFromWatchlist(symbol) {
    return request.delete(`/watchlist/${symbol}`)
  }
}

export default request
