/**
 * Smart Cache Manager with LRU and TTL Support
 *
 * Provides intelligent caching for API responses and computed values.
 */

interface CacheEntry<T = any> {
  value: T
  timestamp: number
  accessCount: number
  ttl?: number
  dependencies?: string[]
}

interface CacheOptions {
  ttl?: number | string // milliseconds or '5m', '1h', '1d'
  maxSize?: number
  persistToStorage?: boolean
  storageKey?: string
  dependencies?: string[]
  refreshAhead?: boolean // Refresh before expiration
}

interface CacheStats {
  hits: number
  misses: number
  sets: number
  deletes: number
  evictions: number
  size: number
  maxSize: number
  hitRate: number
}

interface CacheConfig {
  defaultTTL: number
  maxSize: number
  cleanupInterval: number
  storagePrefix: string
  enableMetrics: boolean
  refreshAheadThreshold: number // Refresh when TTL < this threshold
}

/**
 * LRU Cache with TTL support
 */
export class LRUCache<T = any> {
  private cache = new Map<string, CacheEntry<T>>()
  private accessOrder = new Map<string, number>()
  private accessCounter = 0
  private cleanupTimer?: NodeJS.Timeout
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    sets: 0,
    deletes: 0,
    evictions: 0,
    size: 0,
    maxSize: 0,
    hitRate: 0
  }

  constructor(
    private options: CacheOptions = {},
    private config: Partial<CacheConfig> = {}
  ) {
    this.loadFromStorage()
    this.startCleanup()
  }

  /**
   * Set cache entry
   */
  set(key: string, value: T, options: CacheOptions = {}): void {
    const ttl = this.parseTTL(options.ttl || this.options.ttl || this.config.defaultTTL)
    const now = Date.now()

    // Remove old entry if exists
    if (this.cache.has(key)) {
      this.delete(key)
    }

    // Evict if necessary
    while (this.cache.size >= (options.maxSize || this.options.maxSize || this.config.maxSize || 100)) {
      this.evictLRU()
    }

    const entry: CacheEntry<T> = {
      value,
      timestamp: now,
      accessCount: 0,
      ttl: ttl ? now + ttl : undefined,
      dependencies: options.dependencies
    }

    this.cache.set(key, entry)
    this.accessOrder.set(key, this.accessCounter++)
    this.stats.sets++
    this.stats.size = this.cache.size
    this.stats.maxSize = Math.max(this.stats.maxSize, this.cache.size)

    if (options.persistToStorage || this.options.persistToStorage) {
      this.saveToStorage()
    }
  }

  /**
   * Get cache entry
   */
  get(key: string): T | undefined {
    const entry = this.cache.get(key)

    if (!entry) {
      this.stats.misses++
      this.updateHitRate()
      return undefined
    }

    // Check TTL
    if (entry.ttl && entry.ttl < Date.now()) {
      this.delete(key)
      this.stats.misses++
      this.updateHitRate()
      return undefined
    }

    // Update access
    entry.accessCount++
    this.accessOrder.set(key, this.accessCounter++)
    this.stats.hits++
    this.updateHitRate()

    // Check for refresh ahead
    if (this.config.refreshAheadThreshold && entry.ttl) {
      const timeToExpiry = entry.ttl - Date.now()
      if (timeToExpiry < this.config.refreshAheadThreshold) {
        // Trigger async refresh
        this.triggerRefresh(key, entry)
      }
    }

    return entry.value
  }

  /**
   * Get entry with metadata
   */
  getWithMetadata(key: string): { value: T; metadata: CacheEntry<T> } | undefined {
    const entry = this.cache.get(key)
    if (!entry) return undefined

    const value = this.get(key)
    return value !== undefined ? { value, metadata: { ...entry } } : undefined
  }

  /**
   * Check if key exists and is valid
   */
  has(key: string): boolean {
    const entry = this.cache.get(key)
    if (!entry) return false

    if (entry.ttl && entry.ttl < Date.now()) {
      this.delete(key)
      return false
    }

    return true
  }

  /**
   * Delete cache entry
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key)
    this.accessOrder.delete(key)

    if (deleted) {
      this.stats.deletes++
      this.stats.size = this.cache.size
      this.saveToStorage()
    }

    return deleted
  }

  /**
   * Clear all entries
   */
  clear(): void {
    const size = this.cache.size
    this.cache.clear()
    this.accessOrder.clear()
    this.stats.deletes += size
    this.stats.size = 0
    this.saveToStorage()
  }

  /**
   * Evict expired entries
   */
  evictExpired(): number {
    const now = Date.now()
    let evicted = 0

    for (const [key, entry] of this.cache.entries()) {
      if (entry.ttl && entry.ttl < now) {
        this.delete(key)
        evicted++
      }
    }

    return evicted
  }

  /**
   * Evict entries by dependency
   */
  evictByDependency(dependency: string): number {
    let evicted = 0

    for (const [key, entry] of this.cache.entries()) {
      if (entry.dependencies?.includes(dependency)) {
        this.delete(key)
        evicted++
      }
    }

    return evicted
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return { ...this.stats }
  }

  /**
   * Get all keys
   */
  keys(): string[] {
    return Array.from(this.cache.keys()).filter(key => this.has(key))
  }

  /**
   * Get cache size
   */
  get size(): number {
    return this.cache.size
  }

  /**
   * Private methods
   */
  private evictLRU(): void {
    let oldestKey: string | undefined
    let oldestAccess = Infinity

    for (const [key, accessTime] of this.accessOrder.entries()) {
      if (accessTime < oldestAccess) {
        oldestAccess = accessTime
        oldestKey = key
      }
    }

    if (oldestKey) {
      this.delete(oldestKey)
      this.stats.evictions++
    }
  }

  private parseTTL(ttl: number | string | undefined): number | undefined {
    if (!ttl) return undefined
    if (typeof ttl === 'number') return ttl

    const match = ttl.match(/^(\d+)([smhd])$/)
    if (!match) return undefined

    const [, value, unit] = match
    const multipliers: Record<string, number> = {
      s: 1000,
      m: 60 * 1000,
      h: 60 * 60 * 1000,
      d: 24 * 60 * 60 * 1000
    }

    return parseInt(value) * (multipliers[unit] || 0)
  }

  private updateHitRate(): void {
    const total = this.stats.hits + this.stats.misses
    this.stats.hitRate = total > 0 ? (this.stats.hits / total) * 100 : 0
  }

  private triggerRefresh(key: string, entry: CacheEntry<T>): void {
    // This will be handled by the cache decorator
    // Just emit an event for now
    window.dispatchEvent(new CustomEvent('cache:refresh-needed', {
      detail: { key, entry }
    }))
  }

  private startCleanup(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
    }

    this.cleanupTimer = setInterval(() => {
      this.evictExpired()
    }, this.config.cleanupInterval || 60000) // Default: 1 minute
  }

  private saveToStorage(): void {
    if (!this.options.persistToStorage) return

    try {
      const data = JSON.stringify({
        cache: Array.from(this.cache.entries()),
        accessOrder: Array.from(this.accessOrder.entries()),
        stats: this.stats
      })

      localStorage.setItem(
        this.options.storageKey || this.config.storagePrefix || 'cache',
        data
      )
    } catch (error) {
      console.warn('Cache: Failed to save to localStorage', error)
    }
  }

  private loadFromStorage(): void {
    if (!this.options.persistToStorage) return

    try {
      const data = localStorage.getItem(
        this.options.storageKey || this.config.storagePrefix || 'cache'
      )

      if (!data) return

      const parsed = JSON.parse(data)

      // Restore cache
      this.cache = new Map(parsed.cache || [])
      this.accessOrder = new Map(parsed.accessOrder || [])
      this.stats = { ...this.stats, ...(parsed.stats || {}) }
      this.stats.size = this.cache.size
      this.stats.maxSize = Math.max(this.stats.maxSize, this.cache.size)

      // Evict expired entries
      this.evictExpired()
    } catch (error) {
      console.warn('Cache: Failed to load from localStorage', error)
    }
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
    }
    this.clear()
  }
}

/**
 * Global cache instances
 */
export const globalCaches = new Map<string, LRUCache>()

/**
 * Get or create cache instance
 */
export function getCache<T = any>(
  name: string,
  options?: CacheOptions,
  config?: Partial<CacheConfig>
): LRUCache<T> {
  if (!globalCaches.has(name)) {
    const cache = new LRUCache<T>(options, {
      defaultTTL: 5 * 60 * 1000, // 5 minutes
      maxSize: 100,
      cleanupInterval: 60 * 1000, // 1 minute
      storagePrefix: `cache:${name}`,
      enableMetrics: true,
      refreshAheadThreshold: 30 * 1000, // 30 seconds
      ...config
    })
    globalCaches.set(name, cache)
  }

  return globalCaches.get(name) as LRUCache<T>
}

/**
 * Cache decorator for functions
 */
export function cached<T extends (...args: any[]) => Promise<any>>(
  options: CacheOptions & {
    keyGenerator?: (...args: Parameters<T>) => string
    cache?: string
  } = {}
) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value as T
    const cacheName = options.cache || propertyName
    const cache = getCache(cacheName, options)

    descriptor.value = async function (...args: Parameters<T>): Promise<ReturnType<T>> {
      const key = options.keyGenerator
        ? options.keyGenerator(...args)
        : JSON.stringify(args)

      // Check cache first
      const cached = cache.get(key)
      if (cached !== undefined) {
        return cached
      }

      // Execute and cache result
      try {
        const result = await method.apply(this, args)
        cache.set(key, result, options)
        return result
      } catch (error) {
        // Don't cache errors
        throw error
      }
    } as T

    // Add cache control methods
    descriptor.value.clearCache = function () {
      cache.clear()
    }

    descriptor.value.invalidate = function (...args: Parameters<T>) {
      const key = options.keyGenerator
        ? options.keyGenerator(...args)
        : JSON.stringify(args)
      return cache.delete(key)
    }

    descriptor.value.getStats = function () {
      return cache.getStats()
    }

    return descriptor
  }
}

/**
 * Memoization decorator for pure functions
 */
export function memoize<T extends (...args: any[]) => any>(
  options: CacheOptions & {
    keyGenerator?: (...args: Parameters<T>) => string
    maxSize?: number
  } = {}
) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value as T
    const cache = new LRUCache<ReturnType<T>>({
      maxSize: options.maxSize || 50,
      ttl: options.ttl || 0 // No expiration by default
    })

    descriptor.value = function (...args: Parameters<T>): ReturnType<T> {
      const key = options.keyGenerator
        ? options.keyGenerator(...args)
        : JSON.stringify(args)

      const cached = cache.get(key)
      if (cached !== undefined) {
        return cached
      }

      const result = method.apply(this, args)
      cache.set(key, result)
      return result
    } as T

    return descriptor
  }
}

/**
 * React hook for caching
 */
export function useCache<T = any>(
  name: string,
  options?: CacheOptions,
  config?: Partial<CacheConfig>
) {
  const cache = getCache<T>(name, options, config)

  return {
    get: cache.get.bind(cache),
    set: cache.set.bind(cache),
    has: cache.has.bind(cache),
    delete: cache.delete.bind(cache),
    clear: cache.clear.bind(cache),
    stats: cache.getStats.bind(cache),
    size: cache.size,
    keys: cache.keys.bind(cache)
  }
}

/**
 * Cache analytics
 */
export class CacheAnalytics {
  private static instance: CacheAnalytics
  private metrics = new Map<string, CacheStats>()

  static getInstance(): CacheAnalytics {
    if (!CacheAnalytics.instance) {
      CacheAnalytics.instance = new CacheAnalytics()
    }
    return CacheAnalytics.instance
  }

  recordStats(name: string, stats: CacheStats): void {
    this.metrics.set(name, { ...stats })
  }

  getAnalytics(): {
    totalHits: number
    totalMisses: number
    totalEvictions: number
    averageHitRate: number
    cacheMetrics: Array<{ name: string; stats: CacheStats }>
  } {
    const caches = Array.from(this.metrics.entries())
    const totalHits = caches.reduce((sum, [, stats]) => sum + stats.hits, 0)
    const totalMisses = caches.reduce((sum, [, stats]) => sum + stats.misses, 0)
    const totalEvictions = caches.reduce((sum, [, stats]) => sum + stats.evictions, 0)
    const averageHitRate = totalHits + totalMisses > 0
      ? (totalHits / (totalHits + totalMisses)) * 100
      : 0

    return {
      totalHits,
      totalMisses,
      totalEvictions,
      averageHitRate,
      cacheMetrics: caches.map(([name, stats]) => ({ name, stats }))
    }
  }

  exportReport(): string {
    const analytics = this.getAnalytics()
    return JSON.stringify(analytics, null, 2)
  }

  clear(): void {
    this.metrics.clear()
  }
}

// Auto-cleanup on page unload
window.addEventListener('beforeunload', () => {
  globalCaches.forEach(cache => cache.destroy())
})

export default LRUCache
