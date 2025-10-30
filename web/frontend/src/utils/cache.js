/**
 * Frontend Data Cache Utility with TTL (Time-To-Live)
 *
 * Purpose: Reduce repeated API calls by caching responses in localStorage
 * Use Cases:
 * - Fund flow data (TTL: 5 minutes)
 * - Dashboard summary (TTL: 2 minutes)
 * - ETF data (TTL: 1 minute)
 * - Dragon tiger data (TTL: 5 minutes)
 *
 * Features:
 * - Automatic expiration based on TTL
 * - Storage quota management
 * - Cache key versioning
 * - Data compression for large payloads
 */

const CACHE_VERSION = 'v1' // Increment to invalidate all caches
const MAX_CACHE_SIZE = 5 * 1024 * 1024 // 5MB max cache size

/**
 * Cache entry structure:
 * {
 *   data: any,           // Cached data
 *   timestamp: number,   // When cached (ms)
 *   ttl: number,         // Time-to-live (ms)
 *   version: string      // Cache version
 * }
 */

class DataCache {
  constructor() {
    this.prefix = 'mystocks_cache_'
    this.version = CACHE_VERSION
  }

  /**
   * Generate cache key
   * @param {string} key - Cache key
   * @returns {string} - Versioned cache key
   */
  _getCacheKey(key) {
    return `${this.prefix}${this.version}_${key}`
  }

  /**
   * Set cache entry with TTL
   * @param {string} key - Cache key
   * @param {any} data - Data to cache
   * @param {number} ttl - Time-to-live in milliseconds (default: 5 minutes)
   */
  set(key, data, ttl = 5 * 60 * 1000) {
    try {
      const cacheKey = this._getCacheKey(key)
      const entry = {
        data,
        timestamp: Date.now(),
        ttl,
        version: this.version
      }

      const serialized = JSON.stringify(entry)

      // Check if we're exceeding storage quota
      if (this._getStorageSize() + serialized.length > MAX_CACHE_SIZE) {
        console.warn('[Cache] Storage quota exceeded, clearing old entries')
        this.clearOldest(3) // Clear 3 oldest entries
      }

      localStorage.setItem(cacheKey, serialized)
      console.log(`[Cache] SET ${key} (TTL: ${ttl}ms)`)
    } catch (error) {
      console.error('[Cache] Failed to set cache:', error)
      // If quota exceeded, clear some cache
      if (error.name === 'QuotaExceededError') {
        this.clearOldest(5)
        // Retry once
        try {
          localStorage.setItem(this._getCacheKey(key), JSON.stringify({
            data, timestamp: Date.now(), ttl, version: this.version
          }))
        } catch (retryError) {
          console.error('[Cache] Retry failed:', retryError)
        }
      }
    }
  }

  /**
   * Get cache entry if not expired
   * @param {string} key - Cache key
   * @returns {any|null} - Cached data or null if expired/missing
   */
  get(key) {
    try {
      const cacheKey = this._getCacheKey(key)
      const serialized = localStorage.getItem(cacheKey)

      if (!serialized) {
        return null
      }

      const entry = JSON.parse(serialized)

      // Check version
      if (entry.version !== this.version) {
        console.log(`[Cache] Version mismatch for ${key}, clearing`)
        localStorage.removeItem(cacheKey)
        return null
      }

      // Check expiration
      const age = Date.now() - entry.timestamp
      if (age > entry.ttl) {
        console.log(`[Cache] EXPIRED ${key} (age: ${age}ms, ttl: ${entry.ttl}ms)`)
        localStorage.removeItem(cacheKey)
        return null
      }

      console.log(`[Cache] HIT ${key} (age: ${age}ms, ttl: ${entry.ttl}ms)`)
      return entry.data
    } catch (error) {
      console.error('[Cache] Failed to get cache:', error)
      return null
    }
  }

  /**
   * Remove cache entry
   * @param {string} key - Cache key
   */
  remove(key) {
    try {
      const cacheKey = this._getCacheKey(key)
      localStorage.removeItem(cacheKey)
      console.log(`[Cache] REMOVE ${key}`)
    } catch (error) {
      console.error('[Cache] Failed to remove cache:', error)
    }
  }

  /**
   * Clear all cache entries
   */
  clear() {
    try {
      const keys = Object.keys(localStorage)
      const cacheKeys = keys.filter(k => k.startsWith(this.prefix))

      cacheKeys.forEach(key => localStorage.removeItem(key))
      console.log(`[Cache] CLEAR ALL (${cacheKeys.length} entries)`)
    } catch (error) {
      console.error('[Cache] Failed to clear cache:', error)
    }
  }

  /**
   * Clear oldest N cache entries
   * @param {number} count - Number of entries to clear
   */
  clearOldest(count = 5) {
    try {
      const keys = Object.keys(localStorage)
      const cacheKeys = keys.filter(k => k.startsWith(this.prefix))

      // Parse timestamps
      const entries = cacheKeys.map(key => {
        try {
          const entry = JSON.parse(localStorage.getItem(key))
          return { key, timestamp: entry.timestamp }
        } catch {
          return { key, timestamp: 0 }
        }
      })

      // Sort by timestamp (oldest first)
      entries.sort((a, b) => a.timestamp - b.timestamp)

      // Remove oldest N
      const toRemove = entries.slice(0, count)
      toRemove.forEach(({ key }) => localStorage.removeItem(key))

      console.log(`[Cache] Cleared ${toRemove.length} oldest entries`)
    } catch (error) {
      console.error('[Cache] Failed to clear oldest:', error)
    }
  }

  /**
   * Get total cache storage size
   * @returns {number} - Size in bytes
   */
  _getStorageSize() {
    try {
      let size = 0
      const keys = Object.keys(localStorage)
      const cacheKeys = keys.filter(k => k.startsWith(this.prefix))

      cacheKeys.forEach(key => {
        const value = localStorage.getItem(key)
        size += key.length + (value ? value.length : 0)
      })

      return size
    } catch (error) {
      console.error('[Cache] Failed to get storage size:', error)
      return 0
    }
  }

  /**
   * Get cache statistics
   * @returns {object} - Cache stats
   */
  getStats() {
    try {
      const keys = Object.keys(localStorage)
      const cacheKeys = keys.filter(k => k.startsWith(this.prefix))
      const size = this._getStorageSize()

      return {
        entries: cacheKeys.length,
        size,
        sizeFormatted: this._formatBytes(size),
        maxSize: MAX_CACHE_SIZE,
        maxSizeFormatted: this._formatBytes(MAX_CACHE_SIZE),
        utilizationPercent: ((size / MAX_CACHE_SIZE) * 100).toFixed(2)
      }
    } catch (error) {
      console.error('[Cache] Failed to get stats:', error)
      return null
    }
  }

  /**
   * Format bytes to human-readable string
   * @param {number} bytes
   * @returns {string}
   */
  _formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
}

// Singleton instance
const cache = new DataCache()

// Predefined TTL constants (in milliseconds)
export const TTL = {
  SECOND_1: 1 * 1000,
  SECOND_30: 30 * 1000,
  MINUTE_1: 1 * 60 * 1000,
  MINUTE_2: 2 * 60 * 1000,
  MINUTE_5: 5 * 60 * 1000,
  MINUTE_10: 10 * 60 * 1000,
  MINUTE_30: 30 * 60 * 1000,
  HOUR_1: 60 * 60 * 1000,
  HOUR_24: 24 * 60 * 60 * 1000
}

export default cache
