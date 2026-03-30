/**
 * 智能数据服务
 *
 * 基于智能数据源适配器的高级数据获取服务
 * 提供统一的业务数据接口，支持自动降级和缓存
 */

import { intelligentDataSourceAdapter } from './intelligentDataSourceAdapter.js'

class SmartDataService {
  constructor() {
    this.adapter = intelligentDataSourceAdapter
    this.isInitialized = false

    // 监听适配器事件
    this.setupEventListeners()
  }

  /**
   * 设置事件监听器
   */
  setupEventListeners() {
    this.adapter.onModeChange((mode) => {
      this.emit('mode-change', mode)
    })

    this.adapter.onHealthChange((isHealthy) => {
      this.emit('health-change', isHealthy)
    })
  }

  /**
   * 初始化服务
   */
  async initialize() {
    if (this.isInitialized) {
      return
    }

    try {
      // 等待适配器初始化完成
      await new Promise(resolve => setTimeout(resolve, 1000))
      this.isInitialized = true
    } catch (error) {
      console.error('❌ Smart Data Service initialization failed:', error)
      throw error
    }
  }

  /**
   * 事件发射器
   */
  emit(event, data) {
    if (this.listeners && this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Event listener error for ${event}:`, error)
        }
      })
    }
  }

  /**
   * 事件监听器
   */
  on(event, callback) {
    if (!this.listeners) {
      this.listeners = {}
    }
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  off(event, callback) {
    if (this.listeners && this.listeners[event]) {
      const index = this.listeners[event].indexOf(callback)
      if (index > -1) {
        this.listeners[event].splice(index, 1)
      }
    }
  }

  /**
   * Dashboard 相关服务方法
   */
  async getDashboardSummary(userId, options = {}) {
    return this.adapter.getDashboardSummary(userId, options)
  }

  /**
   * Market 数据相关服务方法
   */
  async getMarketQuotes(symbols, options = {}) {
    try {
      const response = await this.adapter.getMarketQuotes(symbols, options)
      return this.normalizeQuotesResponse(response)
    } catch (error) {
      console.error('❌ Failed to get market quotes:', error)
      throw this.createServiceError('获取市场行情失败', error)
    }
  }

  async getFundFlow(options = {}) {
    try {
      const response = await this.adapter.getFundFlow(options)
      return this.normalizeResponse(response)
    } catch (error) {
      console.error('❌ Failed to get fund flow:', error)
      throw this.createServiceError('获取资金流向失败', error)
    }
  }

  async getETFList(options = {}) {
    try {
      const response = await this.adapter.getETFList(options)
      return this.normalizeResponse(response)
    } catch (error) {
      console.error('❌ Failed to get ETF list:', error)
      throw this.createServiceError('获取ETF列表失败', error)
    }
  }

  async getLongHuBang(options = {}) {
    try {
      const response = await this.adapter.getLongHuBang(options)
      return this.normalizeResponse(response)
    } catch (error) {
      console.error('❌ Failed to get longhu bang:', error)
      throw this.createServiceError('获取龙虎榜失败', error)
    }
  }

  /**
   * Stock 数据相关服务方法
   */
  async getStocksBasic(options = {}) {
    try {
      const response = await this.adapter.getStocksBasic(options)
      return this.normalizeResponse(response)
    } catch (error) {
      console.error('❌ Failed to get stocks basic info:', error)
      throw this.createServiceError('获取股票基础信息失败', error)
    }
  }

  async getStocksDaily(options = {}) {
    try {
      const response = await this.adapter.getStocksDaily(options)
      return this.normalizeResponse(response)
    } catch (error) {
      console.error('❌ Failed to get stocks daily data:', error)
      throw this.createServiceError('获取股票日线数据失败', error)
    }
  }

  /**
   * 数据质量监控服务方法
   */
  async getDataQualityHealth() {
    try {
      return await this.adapter.getDataQualityHealth()
    } catch (error) {
      console.error('❌ Failed to get data quality health:', error)
      throw this.createServiceError('获取数据质量健康状态失败', error)
    }
  }

  async getDataQualityMetrics() {
    try {
      return await this.adapter.getDataQualityMetrics()
    } catch (error) {
      console.error('❌ Failed to get data quality metrics:', error)
      throw this.createServiceError('获取数据质量指标失败', error)
    }
  }

  /**
   * 通用数据获取方法
   */
  async fetchCustomData(endpoint, options = {}) {
    try {
      return await this.adapter.fetchData(endpoint, options)
    } catch (error) {
      console.error(`❌ Failed to fetch custom data from ${endpoint}:`, error)
      throw this.createServiceError(`获取自定义数据失败: ${endpoint}`, error)
    }
  }

  /**
   * 响应数据标准化
   */
  normalizeResponse(response) {
    // 统一响应格式
    if (response && response.success !== false) {
      return {
        success: true,
        data: response.data || response,
        source: this.getSourceInfo(response),
        timestamp: new Date().toISOString()
      }
    } else {
      return {
        success: false,
        error: response.error || response.message || 'Unknown error',
        source: this.getSourceInfo(response),
        timestamp: new Date().toISOString()
      }
    }
  }

  normalizeQuotesResponse(response) {
    const normalized = this.normalizeResponse(response)

    if (normalized.success && normalized.data) {
      // 标准化行情数据
      if (Array.isArray(normalized.data.quotes)) {
        normalized.data.quotes = normalized.data.quotes.map(quote => ({
          ...quote,
          symbol: String(quote.symbol || ''),
          name: quote.name || this.getDefaultStockName(quote.symbol),
          current_price: parseFloat(quote.current_price || 0),
          change_percent: parseFloat(quote.change_percent || 0),
          volume: parseInt(quote.volume || 0),
          turnover: parseFloat(quote.turnover || 0),
          timestamp: quote.timestamp || new Date().toISOString()
        }))
      }
    }

    return normalized
  }

  /**
   * 获取数据源信息
   */
  getSourceInfo(response) {
    if (response && response._source) {
      return {
        type: response._source,
        fallback: response._fallback_reason || null
      }
    }

    const status = this.adapter.getStatus()
    return {
      type: status.mode,
      fallback: status.fallbackEnabled ? 'enabled' : 'disabled'
    }
  }

  /**
   * 获取默认股票名称
   */
  getDefaultStockName(symbol) {
    const stockNames = {
      '000001': '平安银行',
      '000002': '万科A',
      '600519': '贵州茅台',
      '000858': '五粮液',
      '600036': '招商银行',
      '600276': '恒瑞医药',
      '002415': '海康威视'
    }
    return stockNames[String(symbol)] || `股票${symbol}`
  }

  /**
   * 创建服务错误
   */
  createServiceError(message, originalError) {
    const error = new Error(message)
    error.originalError = originalError
    error.serviceName = 'SmartDataService'
    error.timestamp = new Date().toISOString()
    error.sourceMode = this.adapter.getStatus().mode
    return error
  }

  /**
   * 服务状态信息
   */
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      adapterStatus: this.adapter.getStatus(),
      lastUpdated: new Date().toISOString()
    }
  }

  /**
   * 服务健康检查
   */
  async healthCheck() {
    try {
      const status = this.getStatus()
      const healthData = await this.getDataQualityHealth()

      return {
        service: status.isInitialized ? 'healthy' : 'initializing',
        adapter: status.adapterStatus.mode,
        sources: healthData.data?.total_sources || 0,
        healthy: healthData.data?.healthy_sources || 0,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return {
        service: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * 清理缓存
   */
  clearCache() {
    this.adapter.clearCache()
  }

  /**
   * 批量获取数据
   */
  async batchFetch(requests, options = {}) {
    const { concurrent = 3 } = options
    const results = []

    // 分批处理请求
    for (let i = 0; i < requests.length; i += concurrent) {
      const batch = requests.slice(i, i + concurrent)
      const batchResults = await Promise.allSettled(
        batch.map(request => {
          return this.fetchCustomData(request.endpoint, request.options)
        })
      )

      // 处理批量结果
      batchResults.forEach((result, index) => {
        results.push({
          request: batch[index],
          result: result.status === 'fulfilled' ? result.value : null,
          error: result.status === 'rejected' ? result.reason : null
        })
      })
    }

    return results
  }

  /**
   * 智能重试机制
   */
  async retryWithBackoff(operation, maxRetries = 3, baseDelay = 1000) {
    let lastError = null

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await operation()
      } catch (error) {
        lastError = error

        if (attempt === maxRetries - 1) {
          break
        }

        // 指数退避延迟
        const delay = baseDelay * Math.pow(2, attempt)
        console.warn(`⚠️ Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`)

        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    throw lastError
  }
}

// 创建全局实例
export const smartDataService = new SmartDataService()

// 导出便捷方法
export default smartDataService
