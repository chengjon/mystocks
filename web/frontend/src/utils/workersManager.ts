/**
 * Web Workers Manager for MyStocks
 * Unified interface for managing Web Workers and technical calculations
 *
 * Features:
 * - Worker lifecycle management (create, terminate, restart)
 * - Technical indicators calculation via dedicated worker
 * - Performance monitoring and error recovery
 * - Batch processing capabilities
 * - Memory management and cleanup
 */

import {
  WorkerMessageType,
  MessagePriority,
  WorkerMessageUtils,
  type WorkerMessage,
  type WorkerResponse,
  type WorkerProgress,
  type WorkerError,
  type WorkerConfig
} from '@/workers/protocol'

export interface TechnicalIndicatorResult {
  indicator: string
  symbol: string
  data: any[]
  metadata: {
    period?: number
    periods: number
    timestamp: number
    calculationTime: number
  }
}

export interface WorkerHealthStatus {
  isAlive: boolean
  lastHeartbeat: number
  memoryUsage?: {
    used: number
    total: number
    limit: number
  }
  supportedIndicators: string[]
  errorCount: number
  uptime: number
}

export class WorkersManager {
  private static instance: WorkersManager
  private workers: Map<string, Worker> = new Map()
  private workerConfigs: Map<string, WorkerConfig> = new Map()
  private healthStatus: Map<string, WorkerHealthStatus> = new Map()
  private messageHandlers: Map<string, Map<string, (response: WorkerResponse) => void>> = new Map()
  private performanceMetrics: Map<string, any> = new Map()
  private isInitialized = false

  private constructor() {
    this.initializeWorkers()
  }

  static getInstance(): WorkersManager {
    if (!WorkersManager.instance) {
      WorkersManager.instance = new WorkersManager()
    }
    return WorkersManager.instance
  }

  /**
   * Initialize all workers
   */
  private async initializeWorkers(): Promise<void> {
    if (this.isInitialized) return

    try {
      // Initialize technical indicators worker
      await this.createWorker('indicator-calculator', '/workers/indicator-calculator.js', {
        maxConcurrency: 3,
        memoryLimit: 100, // MB
        timeout: 30000, // 30 seconds
        enableProgress: true,
        enableHeartbeat: true,
        heartbeatInterval: 30000 // 30 seconds
      })

      this.isInitialized = true
      console.log('🚀 Workers Manager initialized successfully')

    } catch (error) {
      console.error('❌ Failed to initialize workers:', error)
      throw error
    }
  }

  /**
   * Create and initialize a new worker
   */
  private async createWorker(
    workerId: string,
    workerPath: string,
    config: WorkerConfig
  ): Promise<void> {
    try {
      // Check if worker already exists
      if (this.workers.has(workerId)) {
        await this.terminateWorker(workerId)
      }

      // Create new worker
      const worker = new Worker(workerPath)

      // Set up message handler
      worker.onmessage = (e) => this.handleWorkerMessage(workerId, e.data)
      worker.onerror = (e) => this.handleWorkerError(workerId, e)

      // Store worker and config
      this.workers.set(workerId, worker)
      this.workerConfigs.set(workerId, config)

      // Initialize health status
      this.healthStatus.set(workerId, {
        isAlive: true,
        lastHeartbeat: Date.now(),
        supportedIndicators: [],
        errorCount: 0,
        uptime: Date.now()
      })

      // Wait for worker ready signal
      await this.waitForWorkerReady(workerId)

      console.log(`✅ Worker '${workerId}' created and ready`)

    } catch (error) {
      console.error(`❌ Failed to create worker '${workerId}':`, error)
      throw error
    }
  }

  /**
   * Wait for worker to signal it's ready
   */
  private async waitForWorkerReady(workerId: string, timeout: number = 5000): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Worker '${workerId}' failed to initialize within ${timeout}ms`))
      }, timeout)

      const readyHandler = (response: WorkerResponse) => {
        if (response.type === WorkerMessageType.READY) {
          clearTimeout(timeoutId)

          const status = this.healthStatus.get(workerId)
          if (status && response.result?.supportedIndicators) {
            status.supportedIndicators = response.result.supportedIndicators
          }

          resolve()
        }
      }

      // Store temporary handler
      if (!this.messageHandlers.has(workerId)) {
        this.messageHandlers.set(workerId, new Map())
      }
      this.messageHandlers.get(workerId)!.set('__ready__', readyHandler)
    })
  }

  /**
   * Handle messages from workers
   */
  private handleWorkerMessage(workerId: string, message: WorkerMessage): void {
    try {
      const status = this.healthStatus.get(workerId)
      if (!status) return

      switch (message.type) {
        case WorkerMessageType.READY:
          console.log(`📡 Worker '${workerId}' signaled ready`)
          break

        case WorkerMessageType.HEARTBEAT:
          status.lastHeartbeat = Date.now()
          if (message.payload?.memoryUsage) {
            status.memoryUsage = message.payload.memoryUsage
          }
          break

        case WorkerMessageType.PROGRESS:
          this.handleProgressMessage(workerId, message as WorkerProgress)
          break

        case WorkerMessageType.ERROR:
          this.handleErrorMessage(workerId, message as WorkerError)
          break

        default:
          this.handleResponseMessage(workerId, message as WorkerResponse)
          break
      }

    } catch (error) {
      console.error(`❌ Error handling message from worker '${workerId}':`, error)
    }
  }

  /**
   * Handle progress messages
   */
  private handleProgressMessage(workerId: string, progress: WorkerProgress): void {
    const handlers = this.messageHandlers.get(workerId)
    if (!handlers) return

    // Find progress handler for this operation
    const progressHandler = handlers.get(progress.payload?.operationId)
    if (progressHandler) {
      progressHandler(progress as any)
    }

    console.log(`📊 Worker '${workerId}' progress: ${progress.progress}% - ${progress.currentStep || 'Processing'}`)
  }

  /**
   * Handle error messages
   */
  private handleErrorMessage(workerId: string, error: WorkerError): void {
    const status = this.healthStatus.get(workerId)
    if (status) {
      status.errorCount++
    }

    console.error(`❌ Worker '${workerId}' error:`, error.error)

    // Handle recoverable errors
    if (error.recoverable) {
      // Find and call error handler
      const handlers = this.messageHandlers.get(workerId)
      const errorHandler = handlers?.get(error.payload?.operationId)
      if (errorHandler) {
        errorHandler(error as any)
      }
    } else {
      // Non-recoverable error - terminate worker
      console.error(`💀 Non-recoverable error in worker '${workerId}', terminating...`)
      this.terminateWorker(workerId)
    }
  }

  /**
   * Handle response messages
   */
  private handleResponseMessage(workerId: string, response: WorkerResponse): void {
    const handlers = this.messageHandlers.get(workerId)
    if (!handlers) return

    const handler = handlers.get(response.id)
    if (handler) {
      handler(response)
      handlers.delete(response.id) // Clean up handler
    }
  }

  /**
   * Handle worker errors
   */
  private handleWorkerError(workerId: string, error: ErrorEvent): void {
    const status = this.healthStatus.get(workerId)
    if (status) {
      status.errorCount++
      status.isAlive = false
    }

    console.error(`💥 Worker '${workerId}' crashed:`, error.message)

    // Attempt to restart worker
    setTimeout(() => {
      console.log(`🔄 Attempting to restart worker '${workerId}'...`)
      this.restartWorker(workerId)
    }, 1000)
  }

  /**
   * Send message to worker and handle response
   */
  private async sendMessage(
    workerId: string,
    message: WorkerMessage,
    timeout?: number
  ): Promise<WorkerResponse> {
    return new Promise((resolve, reject) => {
      const worker = this.workers.get(workerId)
      if (!worker) {
        reject(new Error(`Worker '${workerId}' not found`))
        return
      }

      const actualTimeout = timeout || this.workerConfigs.get(workerId)?.timeout || 30000

      // Set up timeout
      const timeoutId = setTimeout(() => {
        this.cleanupMessageHandler(workerId, message.id)
        reject(new Error(`Worker '${workerId}' operation timed out after ${actualTimeout}ms`))
      }, actualTimeout)

      // Set up response handler
      const responseHandler = (response: WorkerResponse) => {
        clearTimeout(timeoutId)

        if (response.success) {
          // Track performance metrics
          this.trackPerformanceMetrics(workerId, message.type, response.duration || 0)

          resolve(response)
        } else {
          reject(new Error(response.error || 'Unknown worker error'))
        }
      }

      // Store handler
      if (!this.messageHandlers.has(workerId)) {
        this.messageHandlers.set(workerId, new Map())
      }
      this.messageHandlers.get(workerId)!.set(message.id, responseHandler)

      // Send message
      worker.postMessage(message)
    })
  }

  /**
   * Clean up message handler
   */
  private cleanupMessageHandler(workerId: string, messageId: string): void {
    const handlers = this.messageHandlers.get(workerId)
    if (handlers) {
      handlers.delete(messageId)
    }
  }

  /**
   * Track performance metrics
   */
  private trackPerformanceMetrics(workerId: string, operation: string, duration: number): void {
    if (!this.performanceMetrics.has(workerId)) {
      this.performanceMetrics.set(workerId, {
        operations: new Map(),
        totalOperations: 0,
        totalDuration: 0,
        averageDuration: 0
      })
    }

    const metrics = this.performanceMetrics.get(workerId)!
    metrics.totalOperations++
    metrics.totalDuration += duration
    metrics.averageDuration = metrics.totalDuration / metrics.totalOperations

    if (!metrics.operations.has(operation)) {
      metrics.operations.set(operation, { count: 0, totalDuration: 0, averageDuration: 0 })
    }

    const opMetrics = metrics.operations.get(operation)!
    opMetrics.count++
    opMetrics.totalDuration += duration
    opMetrics.averageDuration = opMetrics.totalDuration / opMetrics.count
  }

  /**
   * Calculate technical indicator using worker
   */
  async calculateIndicator(
    indicator: string,
    data: any[],
    params: Record<string, any> = {},
    symbol: string = 'unknown'
  ): Promise<TechnicalIndicatorResult> {
    const startTime = Date.now()

    try {
      const message = WorkerMessageUtils.createMessage(
        WorkerMessageType.CALCULATE_INDICATOR,
        {
          indicatorName: indicator,
          data,
          params
        },
        MessagePriority.NORMAL
      )

      const response = await this.sendMessage('indicator-calculator', message)

      const calculationTime = Date.now() - startTime

      return {
        indicator,
        symbol,
        data: response.result,
        metadata: {
          ...response.result.metadata,
          timestamp: Date.now(),
          calculationTime
        }
      }

    } catch (error) {
      console.error(`❌ Failed to calculate ${indicator} for ${symbol}:`, error)
      throw error
    }
  }

  /**
   * Batch calculate multiple indicators
   */
  async calculateIndicatorsBatch(
    requests: Array<{
      indicator: string
      data: any[]
      params?: Record<string, any>
      symbol?: string
    }>
  ): Promise<TechnicalIndicatorResult[]> {
    const promises = requests.map(request =>
      this.calculateIndicator(
        request.indicator,
        request.data,
        request.params || {},
        request.symbol || 'unknown'
      )
    )

    return Promise.all(promises)
  }

  /**
   * Get worker health status
   */
  getWorkerHealth(workerId: string): WorkerHealthStatus | null {
    return this.healthStatus.get(workerId) || null
  }

  /**
   * Get all workers health status
   */
  getAllWorkersHealth(): Record<string, WorkerHealthStatus> {
    const result: Record<string, WorkerHealthStatus> = {}
    this.healthStatus.forEach((status, workerId) => {
      result[workerId] = status
    })
    return result
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): Record<string, any> {
    const result: Record<string, any> = {}
    this.performanceMetrics.forEach((metrics, workerId) => {
      result[workerId] = {
        ...metrics,
        operations: Object.fromEntries(metrics.operations)
      }
    })
    return result
  }

  /**
   * Restart a worker
   */
  async restartWorker(workerId: string): Promise<void> {
    try {
      await this.terminateWorker(workerId)

      const config = this.workerConfigs.get(workerId)
      if (!config) {
        throw new Error(`No config found for worker '${workerId}'`)
      }

      // Reconstruct worker path from workerId
      const workerPath = `/workers/${workerId}.js`
      await this.createWorker(workerId, workerPath, config)

      console.log(`🔄 Worker '${workerId}' restarted successfully`)

    } catch (error) {
      console.error(`❌ Failed to restart worker '${workerId}':`, error)
      throw error
    }
  }

  /**
   * Terminate a worker
   */
  async terminateWorker(workerId: string): Promise<void> {
    const worker = this.workers.get(workerId)
    if (worker) {
      worker.terminate()
      this.workers.delete(workerId)
      this.healthStatus.delete(workerId)
      this.messageHandlers.delete(workerId)

      console.log(`🛑 Worker '${workerId}' terminated`)
    }
  }

  /**
   * Terminate all workers and cleanup
   */
  async terminateAll(): Promise<void> {
    const workerIds = Array.from(this.workers.keys())
    await Promise.all(workerIds.map(id => this.terminateWorker(id)))

    this.workers.clear()
    this.workerConfigs.clear()
    this.healthStatus.clear()
    this.messageHandlers.clear()
    this.performanceMetrics.clear()
    this.isInitialized = false

    console.log('🧹 All workers terminated and cleaned up')
  }

  /**
   * Check if all workers are healthy
   */
  isHealthy(): boolean {
    return Array.from(this.healthStatus.values()).every(status => status.isAlive)
  }

  /**
   * Get supported indicators
   */
  getSupportedIndicators(): string[] {
    const indicatorWorker = this.healthStatus.get('indicator-calculator')
    return indicatorWorker?.supportedIndicators || []
  }
}

// Export singleton instance
export const workersManager = WorkersManager.getInstance()