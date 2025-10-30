/**
 * Frontend Performance Monitor
 *
 * Purpose: Track API performance, cache metrics, and user interactions
 * Features:
 * - API call timing and statistics
 * - Cache hit/miss tracking
 * - Component render performance
 * - Automatic slow operation alerts
 * - Performance metrics dashboard
 */

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      apiCalls: [],          // { url, duration, timestamp, status, cached }
      cacheStats: {          // Cache hit/miss statistics
        hits: 0,
        misses: 0,
        totalSize: 0
      },
      renderTimes: [],       // { component, duration, timestamp }
      errors: []             // { type, message, timestamp, context }
    }

    this.thresholds = {
      slowApiCall: 1000,     // API calls > 1000ms are considered slow
      slowRender: 200,       // Component renders > 200ms are slow
      maxMetricsAge: 3600000 // Keep metrics for 1 hour (ms)
    }

    this.alertCallbacks = []

    // Auto-cleanup old metrics every 5 minutes
    setInterval(() => this.cleanupOldMetrics(), 5 * 60 * 1000)
  }

  /**
   * Track an API call
   * @param {string} url - API endpoint
   * @param {number} duration - Call duration in ms
   * @param {number} status - HTTP status code
   * @param {boolean} cached - Whether response was from cache
   */
  trackApiCall(url, duration, status = 200, cached = false) {
    const metric = {
      url,
      duration,
      status,
      cached,
      timestamp: Date.now()
    }

    this.metrics.apiCalls.push(metric)

    // Update cache stats
    if (cached) {
      this.metrics.cacheStats.hits++
    } else {
      this.metrics.cacheStats.misses++
    }

    // Alert on slow API calls
    if (duration > this.thresholds.slowApiCall && !cached) {
      this.triggerAlert('slow_api', {
        url,
        duration,
        threshold: this.thresholds.slowApiCall
      })
    }

    console.log(`[Performance] API ${cached ? 'CACHE' : 'CALL'} ${url}: ${duration}ms`)
  }

  /**
   * Track component render time
   * @param {string} component - Component name
   * @param {number} duration - Render duration in ms
   */
  trackRender(component, duration) {
    const metric = {
      component,
      duration,
      timestamp: Date.now()
    }

    this.metrics.renderTimes.push(metric)

    // Alert on slow renders
    if (duration > this.thresholds.slowRender) {
      this.triggerAlert('slow_render', {
        component,
        duration,
        threshold: this.thresholds.slowRender
      })
    }

    console.log(`[Performance] RENDER ${component}: ${duration}ms`)
  }

  /**
   * Track an error
   * @param {string} type - Error type (api, cache, render, etc.)
   * @param {string} message - Error message
   * @param {object} context - Additional context
   */
  trackError(type, message, context = {}) {
    const error = {
      type,
      message,
      context,
      timestamp: Date.now()
    }

    this.metrics.errors.push(error)

    this.triggerAlert('error', error)

    console.error(`[Performance] ERROR ${type}: ${message}`, context)
  }

  /**
   * Update cache statistics
   * @param {object} stats - Cache stats from cache.getStats()
   */
  updateCacheStats(stats) {
    if (stats) {
      this.metrics.cacheStats.totalSize = stats.size
    }
  }

  /**
   * Get API call statistics
   * @param {string} url - Optional URL filter
   * @returns {object} - Statistics object
   */
  getApiStats(url = null) {
    let calls = this.metrics.apiCalls

    if (url) {
      calls = calls.filter(c => c.url.includes(url))
    }

    if (calls.length === 0) {
      return {
        count: 0,
        avgDuration: 0,
        minDuration: 0,
        maxDuration: 0,
        cacheHitRate: 0,
        slowCallCount: 0
      }
    }

    const durations = calls.map(c => c.duration)
    const cachedCalls = calls.filter(c => c.cached).length
    const slowCalls = calls.filter(c => c.duration > this.thresholds.slowApiCall).length

    return {
      count: calls.length,
      avgDuration: (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2),
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      cacheHitRate: ((cachedCalls / calls.length) * 100).toFixed(2),
      slowCallCount: slowCalls
    }
  }

  /**
   * Get cache statistics
   * @returns {object} - Cache statistics
   */
  getCacheStats() {
    const total = this.metrics.cacheStats.hits + this.metrics.cacheStats.misses
    return {
      hits: this.metrics.cacheStats.hits,
      misses: this.metrics.cacheStats.misses,
      total,
      hitRate: total > 0 ? ((this.metrics.cacheStats.hits / total) * 100).toFixed(2) : 0,
      totalSize: this.metrics.cacheStats.totalSize,
      sizeFormatted: this.formatBytes(this.metrics.cacheStats.totalSize)
    }
  }

  /**
   * Get render statistics
   * @param {string} component - Optional component filter
   * @returns {object} - Render statistics
   */
  getRenderStats(component = null) {
    let renders = this.metrics.renderTimes

    if (component) {
      renders = renders.filter(r => r.component === component)
    }

    if (renders.length === 0) {
      return {
        count: 0,
        avgDuration: 0,
        minDuration: 0,
        maxDuration: 0,
        slowRenderCount: 0
      }
    }

    const durations = renders.map(r => r.duration)
    const slowRenders = renders.filter(r => r.duration > this.thresholds.slowRender).length

    return {
      count: renders.length,
      avgDuration: (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2),
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      slowRenderCount: slowRenders
    }
  }

  /**
   * Get all metrics summary
   * @returns {object} - Complete metrics summary
   */
  getMetricsSummary() {
    return {
      api: this.getApiStats(),
      cache: this.getCacheStats(),
      render: this.getRenderStats(),
      errors: {
        count: this.metrics.errors.length,
        recent: this.metrics.errors.slice(-5).reverse()
      },
      timestamp: Date.now()
    }
  }

  /**
   * Register an alert callback
   * @param {function} callback - Callback function (type, data) => void
   */
  onAlert(callback) {
    this.alertCallbacks.push(callback)
  }

  /**
   * Trigger an alert
   * @param {string} type - Alert type
   * @param {object} data - Alert data
   */
  triggerAlert(type, data) {
    this.alertCallbacks.forEach(callback => {
      try {
        callback(type, data)
      } catch (error) {
        console.error('[Performance] Alert callback error:', error)
      }
    })
  }

  /**
   * Clean up metrics older than maxMetricsAge
   */
  cleanupOldMetrics() {
    const now = Date.now()
    const maxAge = this.thresholds.maxMetricsAge

    this.metrics.apiCalls = this.metrics.apiCalls.filter(
      m => now - m.timestamp < maxAge
    )

    this.metrics.renderTimes = this.metrics.renderTimes.filter(
      m => now - m.timestamp < maxAge
    )

    this.metrics.errors = this.metrics.errors.filter(
      m => now - m.timestamp < maxAge
    )

    console.log('[Performance] Old metrics cleaned up')
  }

  /**
   * Reset all metrics
   */
  reset() {
    this.metrics = {
      apiCalls: [],
      cacheStats: {
        hits: 0,
        misses: 0,
        totalSize: 0
      },
      renderTimes: [],
      errors: []
    }
    console.log('[Performance] Metrics reset')
  }

  /**
   * Export metrics as JSON
   * @returns {string} - JSON string
   */
  export() {
    return JSON.stringify(this.getMetricsSummary(), null, 2)
  }

  /**
   * Format bytes to human-readable string
   * @param {number} bytes
   * @returns {string}
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  /**
   * Get performance report for console
   * @returns {string} - Formatted report
   */
  getReport() {
    const summary = this.getMetricsSummary()

    return `
=== Performance Report ===
API Calls:
  Total: ${summary.api.count}
  Avg Duration: ${summary.api.avgDuration}ms
  Cache Hit Rate: ${summary.api.cacheHitRate}%
  Slow Calls: ${summary.api.slowCallCount}

Cache:
  Hits: ${summary.cache.hits}
  Misses: ${summary.cache.misses}
  Hit Rate: ${summary.cache.hitRate}%
  Total Size: ${summary.cache.sizeFormatted}

Renders:
  Total: ${summary.render.count}
  Avg Duration: ${summary.render.avgDuration}ms
  Slow Renders: ${summary.render.slowRenderCount}

Errors:
  Total: ${summary.errors.count}
  Recent: ${summary.errors.recent.length}
========================
`
  }
}

// Singleton instance
const performanceMonitor = new PerformanceMonitor()

// Expose to window for debugging
if (typeof window !== 'undefined') {
  window.performanceMonitor = performanceMonitor
}

export default performanceMonitor
