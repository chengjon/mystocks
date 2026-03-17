/**
 * 智能数据源适配器
 *
 * 功能：
 * 1. 自动检测后端数据源模式（Mock/Real/Hybrid）
 * 2. 智能数据获取和降级处理
 * 3. 数据源健康监控
 * 4. 统一的API接口适配
 * 5. 缓存和性能优化
 */

import { httpClient } from './httpClient.js'

class IntelligentDataSourceAdapter {
  constructor() {
    this.currentMode = 'unknown'
    this.fallbackEnabled = true
    this.healthStatus = {}
    this.lastHealthCheck = null
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5分钟缓存
    this.observers = []

    // 配置选项
    this.config = {
      autoDetectMode: true,
      enableFallback: true,
      enableCache: true,
      healthCheckInterval: 30000, // 30秒
      retryCount: 3,
      retryDelay: 1000
    }

    // 初始化
    this.initialize()
  }

  /**
   * 初始化适配器
   */
  async initialize() {
    try {
      await this.detectDataSourceMode()
      this.startHealthMonitoring()
      console.log('✅ Intelligent Data Source Adapter initialized')
    } catch (error) {
      console.error('❌ Failed to initialize Data Source Adapter:', error)
    }
  }

  /**
   * 检测数据源模式
   */
  async detectDataSourceMode() {
    try {
      const response = await httpClient.get('/api/data-quality/config/mode')
      const config = response.data

      this.currentMode = config.current_mode
      this.fallbackEnabled = config.fallback_enabled

      console.log(`📊 Data Source Mode: ${this.currentMode}`)
      console.log(`🔄 Fallback Enabled: ${this.fallbackEnabled}`)

      // 通知观察者模式变更
      this.notifyModeChange(this.currentMode)

      return config
    } catch (_error) {
      console.warn('⚠️ Failed to detect data source mode, using default')
      this.currentMode = 'mock'
      this.fallbackEnabled = true
    }
  }

  /**
   * 开始健康监控
   */
  startHealthMonitoring() {
    // 立即检查一次
    this.checkHealthStatus()

    // 定期检查
    setInterval(() => {
      this.checkHealthStatus()
    }, this.config.healthCheckInterval)
  }

  /**
   * 检查健康状态
   */
  async checkHealthStatus() {
    try {
      const response = await httpClient.get('/api/data-quality/health')
      const healthData = response.data

      // 计算总体健康状态
      const totalSources = healthData.data.total_sources
      const healthySources = healthData.data.healthy_sources
      const overallHealth = healthySources === totalSources

      this.lastHealthCheck = {
        timestamp: new Date(),
        overall: overallHealth,
        details: healthData.data
      }

      // 如果健康状态变化，通知观察者
      if (this.healthStatus.overall !== overallHealth) {
        this.notifyHealthChange(overallHealth)
      }

      this.healthStatus = {
        overall: overallHealth,
        ...healthData.data
      }

    } catch (error) {
      console.warn('⚠️ Health check failed:', error)
      this.healthStatus = {
        overall: false,
        timestamp: new Date(),
        error: error.message
      }
    }
  }

  /**
   * 智能数据获取
   * 支持自动重试、缓存和降级
   */
  async fetchData(endpoint, options = {}) {
    const cacheKey = this.generateCacheKey(endpoint, options)

    // 尝试从缓存获取
    if (this.config.enableCache) {
      const cachedData = this.getFromCache(cacheKey)
      if (cachedData) {
        return cachedData
      }
    }

    // 执行数据获取
    let attempt = 0
    let lastError = null

    while (attempt < this.config.retryCount) {
      try {
        const result = await this.performDataRequest(endpoint, options)

        // 缓存成功的结果
        if (this.config.enableCache && result) {
          this.setCache(cacheKey, result)
        }

        return result
      } catch (error) {
        attempt++
        lastError = error

        if (attempt < this.config.retryCount) {
          console.warn(`⚠️ Request failed (attempt ${attempt}), retrying...`, error.message)
          await this.delay(this.config.retryDelay * attempt)
        }
      }
    }

    // 所有重试都失败，尝试降级
    if (this.fallbackEnabled && this.currentMode === 'hybrid') {
      console.warn('🔄 Attempting fallback to mock data')
      return this.getFallbackData(endpoint, options)
    }

    // 最终失败
    throw lastError
  }

  /**
   * 执行实际的数据请求
   */
  async performDataRequest(endpoint, options) {
    const startTime = performance.now()

    try {
      const response = await httpClient.get(endpoint, options)
      const responseTime = performance.now() - startTime

      // 记录性能指标
      this.recordRequestMetrics(endpoint, true, responseTime)

      return response
    } catch (error) {
      const responseTime = performance.now() - startTime
      this.recordRequestMetrics(endpoint, false, responseTime, error.message)
      throw error
    }
  }

  /**
   * 获取降级数据（Mock）
   */
  async getFallbackData(endpoint, options = {}) {
    try {
      // 生成降级的Mock数据
      const mockData = this.generateMockData(endpoint, options)
      return {
        success: true,
        data: mockData,
        _source: 'mock_fallback',
        _fallback_reason: 'Real data request failed'
      }
    } catch (error) {
      throw new Error(`Fallback data generation failed: ${error.message}`)
    }
  }

  /**
   * 生成Mock数据
   */
  generateMockData(endpoint, options) {
    const mockDataGenerators = {
      // Dashboard相关
      '/api/dashboard/market-overview': () => ({
        market_overview: {
          indices: [
            { symbol: '000001', name: '上证指数', current_price: 3200.15, change_percent: 1.2 },
            { symbol: '399001', name: '深证成指', current_price: 10500.23, change_percent: -0.8 }
          ],
          up_count: 2156,
          down_count: 1832,
          total_volume: '8500亿',
          timestamp: new Date().toISOString()
        },
        watchlist: [
          { symbol: '600519', name: '贵州茅台', current_price: 1678.50, change_percent: 2.35 },
          { symbol: '000858', name: '五粮液', current_price: 142.30, change_percent: -1.20 }
        ],
        portfolio: {
          total_market_value: 500000.00,
          total_cost: 450000.00,
          total_profit_loss: 50000.00,
          position_count: 2
        },
        risk_alerts: []
      }),

      // Market相关
      '/api/data/markets/overview': () => ({
        quotes: options.params?.symbols?.split(',').map(symbol => ({
          symbol: symbol.trim(),
          name: this.getStockName(symbol.trim()),
          current_price: Math.random() * 100 + 10,
          change_percent: (Math.random() - 0.5) * 5,
          volume: Math.floor(Math.random() * 1000000),
          timestamp: new Date().toISOString()
        })) || []
      }),

      // 默认Mock数据
      'default': () => ({
        status: 'success',
        data: [],
        message: 'Mock data generated',
        timestamp: new Date().toISOString()
      })
    }

    const generator = mockDataGenerators[endpoint] || mockDataGenerators['default']
    return generator()
  }

  /**
   * 获取股票名称
   */
  getStockName(symbol) {
    const stockNames = {
      '000001': '平安银行',
      '000002': '万科A',
      '600519': '贵州茅台',
      '000858': '五粮液',
      '600036': '招商银行',
      '600276': '恒瑞医药',
      '002415': '海康威视'
    }
    return stockNames[symbol] || `股票${symbol}`
  }

  /**
   * 缓存管理
   */
  generateCacheKey(endpoint, options) {
    const optionsStr = JSON.stringify(options)
    return `${endpoint}:${optionsStr}`
  }

  getFromCache(key) {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  /**
   * 记录请求指标
   */
  recordRequestMetrics(endpoint, success, responseTime, error = null) {
    // 这里可以发送到监控服务或本地存储
    const metrics = {
      endpoint,
      success,
      responseTime,
      error,
      timestamp: new Date(),
      mode: this.currentMode
    }

    console.debug('📊 Request Metrics:', metrics)
  }

  /**
   * 观察者模式 - 模式变更通知
   */
  onModeChange(callback) {
    this.observers.push({ type: 'mode', callback })
  }

  notifyModeChange(mode) {
    this.observers.filter(obs => obs.type === 'mode').forEach(obs => {
      try {
        obs.callback(mode)
      } catch (error) {
        console.error('Observer error:', error)
      }
    })
  }

  /**
   * 观察者模式 - 健康状态变更通知
   */
  onHealthChange(callback) {
    this.observers.push({ type: 'health', callback })
  }

  notifyHealthChange(isHealthy) {
    this.observers.filter(obs => obs.type === 'health').forEach(obs => {
      try {
        obs.callback(isHealthy)
      } catch (error) {
        console.error('Observer error:', error)
      }
    })
  }

  /**
   * 获取当前状态信息
   */
  getStatus() {
    return {
      mode: this.currentMode,
      fallbackEnabled: this.fallbackEnabled,
      health: this.healthStatus,
      lastHealthCheck: this.lastHealthCheck,
      cacheSize: this.cache.size,
      config: this.config
    }
  }

  /**
   * 清理缓存
   */
  clearCache() {
    this.cache.clear()
    console.log('🧹 Cache cleared')
  }

  /**
   * 手动切换模式（仅用于测试）
   */
  async forceMode(mode) {
    // 这里可以添加强制切换逻辑
    console.warn(`⚠️ Force mode to ${mode} (for testing only)`)
    await this.detectDataSourceMode()
  }

  /**
   * 工具方法 - 延迟
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * 智能适配器接口 - 为不同数据类型提供专门的方法
   */

  // Dashboard数据
  async getDashboardSummary(userId, options = {}) {
    return this.fetchData('/api/dashboard/market-overview', {
      params: {
        user_id: userId,
        ...options
      }
    })
  }

  // Market数据
  async getMarketQuotes(symbols, options = {}) {
    return this.fetchData(`/api/data/markets/overview?symbols=${symbols}`, options)
  }

  async getFundFlow(options = {}) {
    return this.fetchData('/api/market/fund-flow', options)
  }

  async getETFList(options = {}) {
    return this.fetchData('/api/market/etf/list', options)
  }

  async getLongHuBang(options = {}) {
    return this.fetchData('/api/market/lhb', options)
  }

  // Data数据
  async getStocksBasic(options = {}) {
    const params = new URLSearchParams(options).toString()
    return this.fetchData(`/api/data/stocks/basic?${params}`)
  }

  async getStocksDaily(options = {}) {
    const params = new URLSearchParams(options).toString()
    return this.fetchData(`/api/data/stocks/daily?${params}`)
  }

  // 数据质量监控
  async getDataQualityHealth() {
    return this.fetchData('/api/data-quality/health')
  }

  async getDataQualityMetrics() {
    return this.fetchData('/api/data-quality/metrics')
  }
}

// 创建全局实例
export const intelligentDataSourceAdapter = new IntelligentDataSourceAdapter()

// 导出便捷方法
export default intelligentDataSourceAdapter
