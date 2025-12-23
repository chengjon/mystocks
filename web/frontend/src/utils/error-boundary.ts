/**
 * Error Boundary and Error Handling System
 *
 * Provides comprehensive error catching, reporting, and recovery mechanisms.
 */

import type { App, ComponentPublicInstance } from 'vue'

export interface ErrorInfo {
  componentName?: string
  componentStack?: string
  errorBoundary?: string
  timestamp: number
  userAgent: string
  url: string
  userId?: string
  sessionId: string
  buildVersion?: string
}

export interface ErrorReport {
  id: string
  error: Error
  info: ErrorInfo
  context?: Record<string, any>
  severity: 'low' | 'medium' | 'high' | 'critical'
  resolved: boolean
  reports: number
  firstOccurred: Date
  lastOccurred: Date
}

export interface ErrorBoundaryOptions {
  fallbackComponent?: any
  onError?: (error: Error, info: ErrorInfo) => void
  onRecovery?: (error: Error) => void
  maxRetries?: number
  resetKeys?: Array<string | number>
  reportToService?: boolean
  serviceEndpoint?: string
  severity?: 'low' | 'medium' | 'high' | 'critical'
}

/**
 * Error Reporting Service
 */
export class ErrorReportingService {
  private static instance: ErrorReportingService
  private errorReports = new Map<string, ErrorReport>()
  private pendingReports: ErrorReport[] = []
  private reportQueue: ErrorReport[] = []
  private isReporting = false

  static getInstance(): ErrorReportingService {
    if (!ErrorReportingService.instance) {
      ErrorReportingService.instance = new ErrorReportingService()
    }
    return ErrorReportingService.instance
  }

  /**
   * Report an error
   */
  async report(error: Error, info: Partial<ErrorInfo> = {}, options: {
    context?: Record<string, any>
    severity?: 'low' | 'medium' | 'high' | 'critical'
    reportToService?: boolean
  } = {}): Promise<void> {
    const errorInfo: ErrorInfo = {
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.getSessionId(),
      buildVersion: this.getBuildVersion(),
      ...info
    }

    const errorHash = this.generateErrorHash(error, errorInfo)
    const existingReport = this.errorReports.get(errorHash)

    if (existingReport) {
      // Update existing error
      existingReport.reports++
      existingReport.lastOccurred = new Date()
      existingReport.severity = this.getHigherSeverity(existingReport.severity, options.severity)
    } else {
      // Create new error report
      const report: ErrorReport = {
        id: this.generateId(),
        error,
        info: errorInfo,
        context: options.context,
        severity: options.severity || 'medium',
        resolved: false,
        reports: 1,
        firstOccurred: new Date(),
        lastOccurred: new Date()
      }

      this.errorReports.set(errorHash, report)
    }

    // Queue for reporting
    if (options.reportToService !== false) {
      this.queueReport(this.errorReports.get(errorHash)!)
    }
  }

  /**
   * Get all error reports
   */
  getReports(): ErrorReport[] {
    return Array.from(this.errorReports.values())
  }

  /**
   * Get unresolved errors
   */
  getUnresolvedErrors(): ErrorReport[] {
    return this.getReports().filter(report => !report.resolved)
  }

  /**
   * Get errors by severity
   */
  getErrorsBySeverity(severity: string): ErrorReport[] {
    return this.getReports().filter(report => report.severity === severity)
  }

  /**
   * Mark error as resolved
   */
  resolveError(errorId: string): void {
    const report = Array.from(this.errorReports.values()).find(r => r.id === errorId)
    if (report) {
      report.resolved = true
    }
  }

  /**
   * Clear all reports
   */
  clearReports(): void {
    this.errorReports.clear()
    this.pendingReports = []
    this.reportQueue = []
  }

  /**
   * Generate error report for external service
   */
  private async sendToService(report: ErrorReport): Promise<void> {
    try {
      const payload = {
        id: report.id,
        message: report.error.message,
        stack: report.error.stack,
        info: report.info,
        context: report.context,
        severity: report.severity,
        reports: report.reports,
        firstOccurred: report.firstOccurred.toISOString(),
        lastOccurred: report.lastOccurred.toISOString()
      }

      // Send to error reporting service
      const endpoint = process.env.VUE_APP_ERROR_REPORTING_ENDPOINT || '/api/errors'
      await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
    } catch (error) {
      console.error('Failed to send error report:', error)
      // Re-queue for later
      this.queueReport(report)
    }
  }

  /**
   * Queue report for sending
   */
  private queueReport(report: ErrorReport): void {
    this.reportQueue.push(report)
    this.processQueue()
  }

  /**
   * Process report queue
   */
  private async processQueue(): Promise<void> {
    if (this.isReporting || this.reportQueue.length === 0) return

    this.isReporting = true

    try {
      while (this.reportQueue.length > 0) {
        const report = this.reportQueue.shift()!
        await this.sendToService(report)
        // Add delay to avoid overwhelming the service
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    } catch (error) {
      console.error('Error processing report queue:', error)
    } finally {
      this.isReporting = false
    }
  }

  /**
   * Generate error hash
   */
  private generateErrorHash(error: Error, info: ErrorInfo): string {
    const key = `${error.name}:${error.message}:${info.componentName || ''}`
    return btoa(key).replace(/[^a-zA-Z0-9]/g, '').substr(0, 16)
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  /**
   * Get session ID
   */
  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('sessionId')
    if (!sessionId) {
      sessionId = this.generateId()
      sessionStorage.setItem('sessionId', sessionId)
    }
    return sessionId
  }

  /**
   * Get build version
   */
  private getBuildVersion(): string {
    return (window as any).__BUILD_VERSION__ || process.env.VUE_APP_VERSION || 'unknown'
  }

  /**
   * Get higher severity
   */
  private getHigherSeverity(
    current: 'low' | 'medium' | 'high' | 'critical',
    new?: 'low' | 'medium' | 'high' | 'critical'
  ): 'low' | 'medium' | 'high' | 'critical' {
    const severityLevels = { low: 1, medium: 2, high: 3, critical: 4 }
    const currentLevel = severityLevels[current]
    const newLevel = new ? severityLevels[new] : currentLevel

    return newLevel > currentLevel ? new! : current
  }
}

/**
 * Vue Error Boundary Mixin
 */
export const ErrorBoundaryMixin = {
  data() {
    return {
      hasError: false,
      error: null as Error | null,
      errorInfo: null as ErrorInfo | null,
      retryCount: 0
    }
  },

  errorCaptured(error: Error, instance: ComponentPublicInstance, info: string) {
    this.hasError = true
    this.error = error
    this.errorInfo = {
      componentName: instance.$options.name || 'Unknown',
      componentStack: info,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: ErrorReportingService.getInstance().getSessionId()
    }

    // Report error
    ErrorReportingService.getInstance().report(error, this.errorInfo, {
      severity: (this as any).$options.errorBoundary?.severity || 'medium'
    })

    // Call custom error handler
    const errorHandler = (this as any).$options.errorBoundary?.onError
    if (errorHandler) {
      errorHandler(error, this.errorInfo)
    }

    // Prevent error from propagating further
    return false
  },

  methods: {
    retry() {
      const maxRetries = (this as any).$options.errorBoundary?.maxRetries || 3
      if (this.retryCount < maxRetries) {
        this.retryCount++
        this.hasError = false
        this.error = null
        this.errorInfo = null

        // Call recovery handler
        const recoveryHandler = (this as any).$options.errorBoundary?.onRecovery
        if (recoveryHandler && this.error) {
          recoveryHandler(this.error)
        }

        // Force re-render
        this.$forceUpdate()
      }
    },

    reset() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
      this.retryCount = 0
    }
  }
}

/**
 * Global Error Handler
 */
export class GlobalErrorHandler {
  private static instance: GlobalErrorHandler
  private originalHandlers: {
    onerror?: any
    onunhandledrejection?: any
  } = {}

  static getInstance(): GlobalErrorHandler {
    if (!GlobalErrorHandler.instance) {
      GlobalErrorHandler.instance = new GlobalErrorHandler()
    }
    return GlobalErrorHandler.instance
  }

  /**
   * Setup global error handlers
   */
  setup(app: App): void {
    // Store original handlers
    this.originalHandlers.onerror = window.onerror
    this.originalHandlers.onunhandledrejection = window.onunhandledrejection

    // Setup Vue error handler
    app.config.errorHandler = (error, instance, info) => {
      const errorInfo: ErrorInfo = {
        componentName: instance?.$options.name || 'Unknown',
        componentStack: info,
        errorBoundary: 'global',
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: ErrorReportingService.getInstance().getSessionId()
      }

      ErrorReportingService.getInstance().report(error, errorInfo, {
        severity: 'high'
      })
    }

    // Setup window error handler
    window.onerror = (message, source, lineno, colno, error) => {
      ErrorReportingService.getInstance().report(
        error || new Error(String(message)),
        {
          componentStack: `${source}:${lineno}:${colno}`,
          errorBoundary: 'window',
          timestamp: Date.now(),
          userAgent: navigator.userAgent,
          url: window.location.href,
          sessionId: ErrorReportingService.getInstance().getSessionId()
        },
        { severity: 'critical' }
      )
    }

    // Setup unhandled promise rejection handler
    window.onunhandledrejection = (event) => {
      ErrorReportingService.getInstance().report(
        event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
        {
          componentStack: 'Unhandled Promise Rejection',
          errorBoundary: 'promise',
          timestamp: Date.now(),
          userAgent: navigator.userAgent,
          url: window.location.href,
          sessionId: ErrorReportingService.getInstance().getSessionId()
        },
        { severity: 'high' }
      )

      // Prevent default browser behavior
      event.preventDefault()
    }
  }

  /**
   * Restore original error handlers
   */
  teardown(): void {
    window.onerror = this.originalHandlers.onerror
    window.onunhandledrejection = this.originalHandlers.onunhandledrejection
  }
}

/**
 * Error Recovery Strategies
 */
export class ErrorRecoveryStrategies {
  /**
   * Network error recovery
   */
  static async recoverNetworkError(error: Error): Promise<void> {
    // Check network connectivity
    if (!navigator.onLine) {
      // Wait for network to be restored
      await new Promise(resolve => {
        const handleOnline = () => {
          window.removeEventListener('online', handleOnline)
          resolve()
        }
        window.addEventListener('online', handleOnline)
      })
    }

    // Clear potentially corrupted caches
    if ('caches' in window) {
      const cacheNames = await caches.keys()
      await Promise.all(cacheNames.map(name => caches.delete(name)))
    }
  }

  /**
   * Memory error recovery
   */
  static recoverMemoryError(): void {
    // Clear caches
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => caches.delete(name))
      })
    }

    // Force garbage collection if available
    if ('gc' in window) {
      (window as any).gc()
    }

    // Reload page if memory is critically low
    if ('memory' in performance) {
      const memory = (performance as any).memory
      if (memory.usedJSHeapSize / memory.totalJSHeapSize > 0.9) {
        window.location.reload()
      }
    }
  }

  /**
   * Component error recovery
   */
  static recoverComponentError(component: ComponentPublicInstance): void {
    // Reset component state
    if ('$reset' in component) {
      (component as any).$reset()
    }

    // Clear component's data
    Object.keys(component.$data).forEach(key => {
      (component as any)[key] = null
    })

    // Force re-render
    component.$forceUpdate()
  }
}

/**
 * Error Boundary Component (Vue 3)
 */
import { defineComponent, ref, onErrorCaptured } from 'vue'

export const ErrorBoundary = defineComponent({
  name: 'ErrorBoundary',
  props: {
    fallbackComponent: {
      type: Object,
      default: null
    },
    maxRetries: {
      type: Number,
      default: 3
    },
    onError: {
      type: Function,
      default: null
    },
    onRecovery: {
      type: Function,
      default: null
    }
  },

  setup(props, { slots }) {
    const hasError = ref(false)
    const error = ref<Error | null>(null)
    const retryCount = ref(0)

    onErrorCaptured((err: Error) => {
      hasError.value = true
      error.value = err

      // Report error
      ErrorReportingService.getInstance().report(err, {
        componentName: 'ErrorBoundary',
        errorBoundary: 'vue',
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: ErrorReportingService.getInstance().getSessionId()
      })

      // Call error handler
      if (props.onError) {
        props.onError(err)
      }

      return false
    })

    const retry = () => {
      if (retryCount.value < props.maxRetries) {
        retryCount.value++
        hasError.value = false
        error.value = null

        // Call recovery handler
        if (props.onRecovery && error.value) {
          props.onRecovery(error.value)
        }
      }
    }

    return () => {
      if (hasError.value && props.fallbackComponent) {
        return props.fallbackComponent({
          error: error.value,
          retry,
          retryCount: retryCount.value
        })
      }

      return slots.default?.()
    }
  }
})

/**
 * Initialize error handling system
 */
export function initErrorHandling(app: App): void {
  // Setup global error handler
  GlobalErrorHandler.getInstance().setup(app)

  // Add error reporting to app instance
  app.config.globalProperties.$errorReporter = ErrorReportingService.getInstance()
}

// Default fallback component
export const DefaultErrorFallback = defineComponent({
  name: 'DefaultErrorFallback',
  props: {
    error: {
      type: Error,
      required: true
    },
    retry: {
      type: Function,
      required: true
    },
    retryCount: {
      type: Number,
      default: 0
    }
  },
  setup(props) {
    const showDetails = ref(false)

    return () => (
      <div class="error-boundary-fallback">
        <div class="error-icon">⚠️</div>
        <h2>Something went wrong</h2>
        <p>We're sorry, but something unexpected happened.</p>

        <button onClick={() => props.retry()}>
          {props.retryCount > 0 ? `Try Again (${props.retryCount})` : 'Try Again'}
        </button>

        <button onClick={() => showDetails.value = !showDetails.value}>
          {showDetails.value ? 'Hide' : 'Show'} Details
        </button>

        {showDetails.value && (
          <details class="error-details">
            <summary>Error Details</summary>
            <pre>{props.error.stack}</pre>
          </details>
        )}
      </div>
    )
  }
})

export default {
  ErrorReportingService,
  ErrorBoundaryMixin,
  ErrorBoundary,
  GlobalErrorHandler,
  ErrorRecoveryStrategies,
  DefaultErrorFallback,
  initErrorHandling
}