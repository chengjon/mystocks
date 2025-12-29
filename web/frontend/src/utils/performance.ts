/**
 * Performance Optimization Utilities
 *
 * Provides lazy loading, code splitting, and performance monitoring tools.
 */

import type { ComponentType } from 'vue'

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
  loadingComponent?: ComponentType
  errorComponent?: ComponentType
  timeout?: number
  retry?: boolean
  maxRetries?: number
  preload?: boolean
  prefetch?: boolean
}

/**
 * Component load result
 */
interface LoadComponentResult<T> {
  component: T
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
  measureComponent(name: string, fn: () => Promise<any>): Promise<any> {
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
      return (performance as any).memory.usedJSHeapSize
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
          const navEntry = entry as PerformanceNavigationTiming
          console.log('Navigation Performance:', {
            domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
            loadComplete: navEntry.loadEventEnd - navEntry.loadEventStart,
            firstPaint: this.getMetric('first-paint'),
            firstContentfulPaint: this.getMetric('first-contentful-paint')
          })
        } else if (entry.entryType === 'resource') {
          const resourceEntry = entry as PerformanceResourceTiming
          console.log('Resource Performance:', {
            name: resourceEntry.name,
            duration: resourceEntry.duration,
            size: resourceEntry.transferSize
          })
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
  private static cache = new Map<string, any>()

  /**
   * Load component lazily
   */
  static async load<T = ComponentType>(
    loader: () => Promise<{ default: T }>,
    options: LazyComponentOptions = {}
  ): Promise<LoadComponentResult<T>> {
    const cacheKey = loader.toString()

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return {
        component: this.cache.get(cacheKey),
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
          component: null as any,
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
      component: null as any,
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
  static async preload<T = ComponentType>(
    loader: () => Promise<{ default: T }>
  ): Promise<void> {
    try {
      await this.load(loader, { preload: true })
    } catch (error) {
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
export class LazyImageLoader {
  private static observer?: IntersectionObserver
  private static images = new Map<HTMLImageElement, string>()

  /**
   * Setup lazy loading
   */
  static setup(): void {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement
              const src = this.images.get(img)

              if (src) {
                img.src = src
                img.classList.add('loaded')
                this.images.delete(img)
                this.observer?.unobserve(img)
              }
            }
          })
        },
        {
          rootMargin: '50px 0px'
        }
      )
    }
  }

  /**
   * Observe image for lazy loading
   */
  static observe(img: HTMLImageElement, src: string): void {
    if (!this.observer) {
      this.setup()
    }

    // Add placeholder
    img.classList.add('lazy-loading')

    if (this.observer) {
      this.images.set(img, src)
      this.observer.observe(img)
    } else {
      // Fallback: load immediately
      img.src = src
    }
  }

  /**
   * Unobserve image
   */
  static unobserve(img: HTMLImageElement): void {
    if (this.observer) {
      this.observer.unobserve(img)
    }
    this.images.delete(img)
  }

  /**
   * Disconnect observer
   */
  static disconnect(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = undefined
    }
    this.images.clear()
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
    const bundleInfo = (window as any).__BUNDLE_INFO__

    if (bundleInfo) {
      return bundleInfo
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
    return (window as any).__ROUTE_CHUNKS__ || {}
  }

  /**
   * Monitor chunk loading
   */
  static monitorChunkLoading(): void {
    // Override import() to monitor chunk loading
    const originalImport = (window as any).__dynamic_import__ || window.importScripts

    if ('import' in window) {
      // Note: This is a simplified example
      // Real implementation would need to handle the module import system
    }
  }
}

/**
 * Performance optimization decorators
 */
export function performanceMonitor(target: any, propertyName: string, descriptor: PropertyDescriptor) {
  const method = descriptor.value
  const monitor = PerformanceMonitor.getInstance()

  descriptor.value = async function (...args: any[]) {
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
export function throttle<T extends (...args: any[]) => any>(
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
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): T {
  let timer: NodeJS.Timeout

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
  if (process.env.NODE_ENV === 'development') {
    setInterval(() => {
      const metrics = monitor.getAllMetrics()
      console.log('Performance Metrics:', metrics)
    }, 30000)
  }
}

// Auto-initialize
if (typeof window !== 'undefined') {
  initPerformanceMonitoring()
}

export default {
  PerformanceMonitor,
  LazyComponentLoader,
  ResourceLoader,
  LazyImageLoader,
  BundleAnalyzer,
  performanceMonitor,
  throttle,
  debounce,
  FPSMonitor,
  VirtualScrollManager,
  RenderQueue,
  fpsMonitor,
  measureRenderTime
}

export interface PerformanceConfig {
  targetFPS: number;
  enableVirtualization: boolean;
  maxVisibleKLines: number;
  workerEnabled: boolean;
  debounceDelay: number;
}

export const DEFAULT_PERFORMANCE_CONFIG: PerformanceConfig = {
  targetFPS: 60,
  enableVirtualization: true,
  maxVisibleKLines: 500,
  workerEnabled: true,
  debounceDelay: 16
};

export class FPSMonitor {
  private fps = 60;
  private frameCount = 0;
  private lastTime = performance.now();
  private callbacks: Set<(fps: number) => void> = new Set();

  constructor() {
    this.startMonitoring();
  }

  private startMonitoring(): void {
    const measure = () => {
      this.frameCount++;
      const now = performance.now();

      if (now - this.lastTime >= 1000) {
        this.fps = this.frameCount;
        this.frameCount = 0;
        this.lastTime = now;
        this.callbacks.forEach(cb => cb(this.fps));
      }

      requestAnimationFrame(measure);
    };

    requestAnimationFrame(measure);
  }

  getFPS(): number {
    return this.fps;
  }

  onFPSChange(callback: (fps: number) => void): () => void {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  isOptimal(): boolean {
    return this.fps >= 50;
  }

  destroy(): void {
    this.callbacks.clear();
  }
}

export class VirtualScrollManager<T> {
  private items: T[] = [];
  private visibleStart = 0;
  private visibleEnd = 100;
  private itemHeight = 20;
  private containerHeight = 400;
  private bufferSize = 10;

  constructor(config?: { itemHeight?: number; containerHeight?: number; bufferSize?: number }) {
    this.itemHeight = config?.itemHeight ?? 20;
    this.containerHeight = config?.containerHeight ?? 400;
    this.bufferSize = config?.bufferSize ?? 10;
  }

  setItems(items: T[]): void {
    this.items = items;
    this.updateVisibleRange();
  }

  setContainerHeight(height: number): void {
    this.containerHeight = height;
    this.updateVisibleRange();
  }

  scrollTo(offset: number): void {
    this.visibleStart = Math.floor(offset / this.itemHeight);
    this.visibleEnd = Math.min(
      this.visibleStart + Math.ceil(this.containerHeight / this.itemHeight) + this.bufferSize,
      this.items.length
    );
  }

  getVisibleItems(): T[] {
    return this.items.slice(this.visibleStart, this.visibleEnd);
  }

  getVisibleRange(): { start: number; end: number; offset: number } {
    return {
      start: this.visibleStart,
      end: this.visibleEnd,
      offset: this.visibleStart * this.itemHeight
    };
  }

  private updateVisibleRange(): void {
    this.visibleEnd = Math.min(
      this.visibleStart + Math.ceil(this.containerHeight / this.itemHeight) + this.bufferSize,
      this.items.length
    );
  }

  getTotalHeight(): number {
    return this.items.length * this.itemHeight;
  }

  getScrollOffset(): number {
    return this.visibleStart * this.itemHeight;
  }
}

export class RenderQueue {
  private queue: (() => void)[] = [];
  private isProcessing = false;
  private maxBatchSize = 10;
  private delay = 0;

  constructor(config?: { maxBatchSize?: number; delay?: number }) {
    this.maxBatchSize = config?.maxBatchSize ?? 10;
    this.delay = config?.delay ?? 0;
  }

  add(task: () => void): void {
    this.queue.push(task);
    this.process();
  }

  addBatch(tasks: (() => void)[]): void {
    this.queue.push(...tasks);
    this.process();
  }

  private async process(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;

    while (this.queue.length > 0) {
      const batch = this.queue.splice(0, this.maxBatchSize);

      for (const task of batch) {
        task();
      }

      if (this.delay > 0) {
        await new Promise(resolve => setTimeout(resolve, this.delay));
      }
    }

    this.isProcessing = false;
  }

  clear(): void {
    this.queue = [];
  }

  getSize(): number {
    return this.queue.length;
  }
}

export function measureRenderTime(label: string): () => void {
  const start = performance.now();

  return () => {
    const duration = performance.now() - start;
    console.log(`[${label}] 渲染耗时: ${duration.toFixed(2)}ms`);
  };
}

export const fpsMonitor = new FPSMonitor();
