/**
 * Performance Optimization Utilities
 *
 * Provides lazy loading, code splitting, and performance monitoring tools.
 */

import type { Component } from 'vue'
export { LazyImageLoader } from './part-1.lazy-image-loader'

/**
 * Performance metrics interface
 */
export interface PerformanceMetrics {
  componentLoadTime: number
  renderTime: number
  memoryUsage?: number
  bundleSize?: number
  cacheHitRate?: number
}

/**
 * Lazy load component with loading and error states
 */
export interface LazyComponentOptions {
  loadingComponent?: Component
  errorComponent?: Component
  timeout?: number
  retry?: boolean
  maxRetries?: number
  preload?: boolean
  prefetch?: boolean
}

/**
 * Result of loading a component
 */
export interface LoadComponentResult<T = Component> {
  component: T | null
  loading: boolean
  error: Error | null
  retry: () => void
}

/**
 * Performance monitor
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics = new Map<string, PerformanceMetrics>()
  private observers = new Set<PerformanceObserver>()

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  /**
   * Measure component load performance
   */
  measureComponent(name: string, fn: () => Promise<unknown>): Promise<unknown> {
    const startTime = performance.now()
    const startMemory = this.getMemoryUsage()

    return fn().then(result => {
      const endTime = performance.now()
      const endMemory = this.getMemoryUsage()

      const metrics: PerformanceMetrics = {
        componentLoadTime: endTime - startTime,
        renderTime: 0, // Will be measured separately
        memoryUsage: endMemory && startMemory ? endMemory - startMemory : undefined
      }

      this.metrics.set(name, metrics)
      return result
    })
  }

  /**
   * Measure render performance
   */
  measureRender(name: string): () => void {
    const startTime = performance.now()

    return () => {
      const endTime = performance.now()
      const existing = this.metrics.get(name) || { componentLoadTime: 0, renderTime: 0 }

      this.metrics.set(name, {
        ...existing,
        renderTime: endTime - startTime
      })
    }
  }

  /**
   * Get metrics for a component
   */
  getMetrics(name: string): PerformanceMetrics | undefined {
    return this.metrics.get(name)
  }

  /**
   * Get all metrics
   */
  getAllMetrics(): Record<string, PerformanceMetrics> {
    const result: Record<string, PerformanceMetrics> = {}
    this.metrics.forEach((value, key) => {
      result[key] = value
    })
    return result
  }

  /**
   * Get memory usage
   */
  getMemoryUsage(): number | undefined {
    if ('memory' in performance) {
      return (performance as unknown as { memory: { usedJSHeapSize: number } }).memory.usedJSHeapSize
    }
    return undefined
  }

  /**
   * Monitor network performance
   */
  monitorNetwork(): void {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'navigation') {
          const _navEntry = entry as PerformanceNavigationTiming
        } else if (entry.entryType === 'resource') {
          const _resourceEntry = entry as PerformanceResourceTiming
        }
      })
    })

    observer.observe({ entryTypes: ['navigation', 'resource'] })
    this.observers.add(observer)
  }

  /**
   * Monitor long tasks
   */
  monitorLongTasks(): void {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          console.warn('Long task detected:', {
            duration: entry.duration,
            startTime: entry.startTime
          })
        })
      })

      observer.observe({ entryTypes: ['longtask'] })
      this.observers.add(observer)
    }
  }

  /**
   * Get specific metric
   */
  private getMetric(name: string): number | undefined {
    const entries = performance.getEntriesByName(name)
    return entries.length > 0 ? entries[0].startTime : undefined
  }

  /**
   * Cleanup
   */
  cleanup(): void {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
  }
}

/**
 * Lazy component loader with retry and error handling
 */
export class LazyComponentLoader {
  private static cache = new Map<string, unknown>()

  /**
   * Load component lazily
   */
  static async load<T = Component>(
    loader: () => Promise<{ default: T }>,
    options: LazyComponentOptions = {}
  ): Promise<LoadComponentResult<T>> {
    const cacheKey = loader.toString()

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return {
        component: this.cache.get(cacheKey) as T | null,
        loading: false,
        error: null,
        retry: () => {}
      }
    }

    let retryCount = 0
    const maxRetries = options.maxRetries || 3

    const attemptLoad = async (): Promise<LoadComponentResult<T>> => {
      try {
        // Setup timeout
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Load timeout')), options.timeout || 10000)
        })

        // Load component
        const loadPromise = loader()
        const module = await Promise.race([loadPromise, timeoutPromise]) as { default: T }
        const component = module.default

        // Cache result
        this.cache.set(cacheKey, component)

        return {
          component,
          loading: false,
          error: null,
          retry: () => {}
        }
      } catch (error) {
        retryCount++

        if (retryCount <= maxRetries && options.retry !== false) {
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
          return attemptLoad()
        }

        return {
          component: null as T | null,
          loading: false,
          error: error as Error,
          retry: () => {
            retryCount = 0
            return attemptLoad()
          }
        }
      }
    }

    // Start with loading state
    const initialResult: LoadComponentResult<T> = {
      component: null as T | null,
      loading: true,
      error: null,
      retry: () => {}
    }

    // Start loading
    attemptLoad().then(result => {
      Object.assign(initialResult, result)
    })

    return initialResult
  }

  /**
   * Preload component
   */
  static async preload<T = Component>(
    loader: () => Promise<{ default: T }>
  ): Promise<void> {
    try {
      await this.load(loader, { preload: true })
    } catch (_error) {
      // Ignore preload errors
    }
  }

  /**
   * Prefetch component code
   */
  static prefetch(chunkName: string): void {
    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = `/${chunkName}.js`
    document.head.appendChild(link)
  }

  /**
   * Clear cache
   */
  static clearCache(): void {
    this.cache.clear()
  }
}

/**
 * Resource loading utilities
 */
export class ResourceLoader {
  private static loadedScripts = new Set<string>()
  private static loadedStyles = new Set<string>()

  /**
   * Load script dynamically
   */
  static async loadScript(src: string, options: {
    async?: boolean
    defer?: boolean
    integrity?: string
    crossOrigin?: string
  } = {}): Promise<void> {
    if (this.loadedScripts.has(src)) return

    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = src
      script.async = options.async ?? true
      script.defer = options.defer ?? false

      if (options.integrity) {
        script.integrity = options.integrity
      }
      if (options.crossOrigin) {
        script.crossOrigin = options.crossOrigin
      }

      script.onload = () => {
        this.loadedScripts.add(src)
        resolve()
      }

      script.onerror = () => {
        reject(new Error(`Failed to load script: ${src}`))
      }

      document.head.appendChild(script)
    })
  }

  /**
   * Load style dynamically
   */
  static async loadStyle(href: string, options: {
    media?: string
    integrity?: string
    crossOrigin?: string
  } = {}): Promise<void> {
    if (this.loadedStyles.has(href)) return

    return new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href = href
      link.media = options.media ?? 'all'

      if (options.integrity) {
        link.integrity = options.integrity
      }
      if (options.crossOrigin) {
        link.crossOrigin = options.crossOrigin
      }

      link.onload = () => {
        this.loadedStyles.add(href)
        resolve()
      }

      link.onerror = () => {
        reject(new Error(`Failed to load style: ${href}`))
      }

      document.head.appendChild(link)
    })
  }

  /**
   * Preload critical resources
   */
  static preloadResources(resources: Array<{
    url: string
    type: 'script' | 'style' | 'image' | 'font'
    priority?: 'high' | 'low'
  }>): void {
    resources.forEach(resource => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.href = resource.url

      switch (resource.type) {
        case 'script':
          link.as = 'script'
          break
        case 'style':
          link.as = 'style'
          break
        case 'image':
          link.as = 'image'
          break
        case 'font':
          link.as = 'font'
          link.type = 'font/woff2'
          link.crossOrigin = 'anonymous'
          break
      }

      if (resource.priority === 'high') {
        link.setAttribute('importance', 'high')
      }

      document.head.appendChild(link)
    })
  }
}

/**
 * Image lazy loading with intersection observer
 */
