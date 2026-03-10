/**
 * Performance Optimization Utilities
 *
 * Provides lazy loading, code splitting, and performance monitoring tools.
 */

import type { Component } from 'vue'

/**
 * Performance Monitor class
 */
class PerformanceMonitor {
  private static instance: PerformanceMonitor

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  measureRender(name: string): () => void {
    const start = performance.now()
    return () => {
      const end = performance.now()
      console.log(`${name} took ${end - start}ms`)
    }
  }

  monitorNetwork(): void {
    // Implementation
  }

  monitorLongTasks(): void {
    // Implementation
  }

  getAllMetrics(): Record<string, unknown> {
    return {}
  }
}

/**
 * Lazy Image Loader class
 */
class LazyImageLoader {
  static setup(): void {
    // Implementation
  }
}

/**
 * Lazy Component Loader class
 */
class LazyComponentLoader {
  static load(component: Component): Promise<Component> {
    return Promise.resolve(component)
  }
}

/**
 * Resource Loader class
 */
class ResourceLoader {
  static load(url: string): Promise<unknown> {
    return fetch(url).then(r => r.json())
  }
}

/**
 * Bundle analyzer utilities
 */
export class BundleAnalyzer {
  /**
   * Get bundle size information
   */
  static async getBundleInfo(): Promise<{
    bundles: Array<{
      name: string
      size: number
      gzipSize?: number
      chunks: string[]
    }>
    totalSize: number
  }> {
    // This would typically be injected by the build process
    const bundleInfo = (window as unknown as Record<string, unknown>).__BUNDLE_INFO__

    if (bundleInfo && typeof bundleInfo === 'object' && 'bundles' in bundleInfo && 'totalSize' in bundleInfo) {
      return bundleInfo as {
        bundles: Array<{
          name: string
          size: number
          gzipSize?: number
          chunks: string[]
        }>
        totalSize: number
      }
    }

    // Fallback: analyze loaded scripts
    const scripts = Array.from(document.querySelectorAll('script[src]'))
    let totalSize = 0

    const bundles = scripts.map(script => {
      const src = script.getAttribute('src') || ''
      const name = src.split('/').pop() || 'unknown'
      // Note: Actual size would need to be fetched or pre-calculated
      const size = 0

      totalSize += size
      return { name, size, chunks: [] }
    })

    return { bundles, totalSize }
  }

  /**
   * Analyze route chunks
   */
  static async getRouteChunks(): Promise<Record<string, string[]>> {
    // This would be provided by the build system
    const routeChunks = (window as unknown as Record<string, unknown>).__ROUTE_CHUNKS__
    return (typeof routeChunks === 'object' && routeChunks !== null ? routeChunks : {}) as Record<string, string[]>
  }

  /**
   * Monitor chunk loading
   */
  static monitorChunkLoading(): void {
    // Override import() to monitor chunk loading
    // Use any type since importScripts is a Web Worker API
    const _originalImport = (window as unknown as Record<string, unknown>).__dynamic_import__ || (window as unknown as Record<string, unknown>).importScripts

    if ('import' in window) {
      // Note: This is a simplified example
      // Real implementation would need to handle the module import system
    }
  }
}

/**
 * Performance optimization decorators
 */
export function performanceMonitor(
  target: unknown,
  propertyName: string,
  descriptor: PropertyDescriptor
): PropertyDescriptor {
  const method = descriptor.value
  const monitor = PerformanceMonitor.getInstance()

  descriptor.value = async function (...args: unknown[]) {
    const endMeasure = monitor.measureRender(propertyName)
    try {
      const result = await method.apply(this, args)
      endMeasure()
      return result
    } catch (error) {
      endMeasure()
      throw error
    }
  }

  return descriptor
}

/**
 * Throttle function execution
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): T {
  let lastCall = 0

  return ((...args: Parameters<T>) => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      return fn(...args)
    }
  }) as T
}

/**
 * Debounce function execution
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): T {
  let timer: ReturnType<typeof setTimeout>

  return ((...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }) as T
}

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring(): void {
  const monitor = PerformanceMonitor.getInstance()

  // Monitor various performance aspects
  monitor.monitorNetwork()
  monitor.monitorLongTasks()

  // Setup lazy image loading
  LazyImageLoader.setup()

  // Log performance metrics
  if (import.meta.env.DEV) {
    setInterval(() => {
      const metrics = monitor.getAllMetrics()
      console.log('Performance Metrics:', metrics)
    }, 30000)
  }
}

export default {
  PerformanceMonitor,
  LazyComponentLoader,
  ResourceLoader,
  LazyImageLoader,
  BundleAnalyzer,
  performanceMonitor,
  throttle,
  debounce
}
