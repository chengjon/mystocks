import type { CacheStats } from './part-1.ts'

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
