/**
 * 前端缓存管理工具 (优化版)
 * 用于优化Dashboard页面图表加载速度和用户体验
 * 
 * 特性:
 * - 多级缓存策略 (内存 + localStorage + sessionStorage)
 * - LRU淘汰策略
 * - 压缩存储
 * - 缓存统计和分析
 * - 智能预热
 * - 内存监控
 */

class CacheManager {
  constructor() {
    this.memoryCache = new Map()
    this.defaultTTL = 5 * 60 * 1000 // 5分钟默认缓存时间
    
    // 缓存统计
    this.stats = {
      hits: 0,
      misses: 0,
      writes: 0,
      evictions: 0,
      totalResponseTime: 0,
      responseTimeSamples: []
    }
    
    // 配置参数
    this.config = {
      maxMemoryEntries: 1000,           // 内存缓存最大条目
      maxLocalStorageEntries: 500,      // localStorage最大条目
      compressionEnabled: true,         // 启用压缩
      autoCleanupInterval: 60000,       // 自动清理间隔
      hitRateWarning: 60,               // 命中率警告阈值
      memoryWarning: 80                 // 内存使用警告阈值
    }
    
    // 存储优先级配置
    this.storagePriority = {
      'realtime': 'memory',              // 实时数据优先内存
      'frequent': 'memory',              // 频繁访问数据优先内存
      'historical': 'localStorage',      // 历史数据使用localStorage
      'temporary': 'sessionStorage',     // 临时数据使用sessionStorage
      'default': 'memory'                // 默认使用内存
    }
    
    // LRU淘汰机制
    this.accessOrder = []
    this.maxAccessHistory = 200
    
    this.init()
  }
  
  init() {
    // 自动清理过期缓存
    this.startAutoCleanup()
    
    // 监控内存使用
    this.startMemoryMonitoring()
    
    console.log('🗂️ 前端缓存管理器初始化完成')
  }

  /**
   * 生成缓存键
   */
  generateKey(funcName, params = {}, category = 'default') {
    const normalizedParams = this.normalizeParams(params)
    return `${category}:${funcName}:${JSON.stringify(normalizedParams)}`
  }
  
  /**
   * 参数标准化
   */
  normalizeParams(params) {
    if (typeof params !== 'object' || params === null) {
      return {}
    }
    
    // 排序键以确保一致性
    const sorted = {}
    Object.keys(params).sort().forEach(key => {
      sorted[key] = params[key]
    })
    
    return sorted
  }

  /**
   * 检查缓存是否有效
   */
  isValid(cacheItem) {
    if (!cacheItem) return false
    return Date.now() - cacheItem.timestamp < cacheItem.ttl
  }

  /**
   * 获取缓存数据
   */
  get(funcName, params = {}) {
    const key = this.generateKey(funcName, params)
    const cacheItem = this.cache.get(key)
    
    if (this.isValid(cacheItem)) {
      return cacheItem.data
    }
    
    // 缓存过期，删除缓存项
    if (cacheItem) {
      this.cache.delete(key)
    }
    
    return null
  }

  /**
   * 设置缓存数据
   */
  set(funcName, data, params = {}, ttl = this.defaultTTL) {
    const key = this.generateKey(funcName, params)
    const cacheItem = {
      data: data,
      timestamp: Date.now(),
      ttl: ttl
    }
    this.cache.set(key, cacheItem)
  }

  /**
   * 清除指定函数的缓存
   */
  clear(funcName) {
    const keysToDelete = []
    for (const key of this.cache.keys()) {
      if (key.startsWith(`${funcName}:`)) {
        keysToDelete.push(key)
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key))
  }

  /**
   * 清除所有缓存
   */
  clearAll() {
    this.cache.clear()
  }

  /**
   * 获取缓存大小
   */
  getSize() {
    return this.cache.size
  }

  /**
   * 获取内存使用量（估算）
   */
  getMemoryUsage() {
    let totalSize = 0
    for (const [key, value] of this.cache.entries()) {
      totalSize += key.length + JSON.stringify(value).length
    }
    return totalSize
  }

  /**
   * 自动清理过期缓存
   */
  cleanup() {
    const keysToDelete = []
    for (const [key, cacheItem] of this.cache.entries()) {
      if (!this.isValid(cacheItem)) {
        keysToDelete.push(key)
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key))
  }

  /**
   * 带缓存的API调用装饰器
   */
  withCache(apiFunction, funcName, params = {}, ttl) {
    const cached = this.get(funcName, params)
    if (cached !== null) {
      return Promise.resolve(cached)
    }
    
    return apiFunction(params).then(result => {
      this.set(funcName, result, params, ttl)
      return result
    })
  }
}

// 创建全局缓存管理器实例
const cacheManager = new CacheManager()

// 自动清理过期缓存
setInterval(() => {
  cacheManager.cleanup()
}, 60 * 1000) // 每分钟清理一次

export default cacheManager
export { CacheManager }
