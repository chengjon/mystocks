
/**
 * 连接健康监控和稳定性管理
 * Connection Health Monitoring and Stability Management
 */

export interface HealthMetrics {
  latency: number
  messageRate: number
  errorRate: number
  uptime: number
  lastActivity: number
}

export interface CircuitBreakerState {
  isOpen: boolean
  failureCount: number
  lastFailureTime: number
  nextRetryTime: number
}

export class ConnectionHealthMonitor {
  private metrics: HealthMetrics = {
    latency: 0,
    messageRate: 0,
    errorRate: 0,
    uptime: 0,
    lastActivity: Date.now()
  }

  private circuitBreaker: CircuitBreakerState = {
    isOpen: false,
    failureCount: 0,
    lastFailureTime: 0,
    nextRetryTime: 0
  }

  private config = {
    circuitBreaker: {
      failureThreshold: 5,
      recoveryTimeout: 60000, // 1分钟
      monitoringWindow: 300000 // 5分钟
    },
    health: {
      maxLatency: 5000, // 5秒
      maxErrorRate: 0.1, // 10%
      minMessageRate: 0.1 // 每分钟至少6条消息
    },
    backpressure: {
      maxQueueSize: 1000,
      batchSize: 50,
      flushInterval: 100
    }
  }

  private messageBuffer: Array<any> = []
  private performanceBuffer: Array<number> = []
  private errorBuffer: Array<number> = []

  constructor(private options: any = {}) {
    // 合并配置
    this.config = { ...this.config, ...options }

    // 启动监控循环
    this.startMonitoring()
  }

  /**
   * 记录成功消息
   */
  recordMessage(latency?: number): void {
    const now = Date.now()

    // 更新最后活动时间
    this.metrics.lastActivity = now

    // 记录延迟
    if (latency !== undefined) {
      this.performanceBuffer.push(latency)
      if (this.performanceBuffer.length > 100) {
        this.performanceBuffer.shift()
      }

      // 计算平均延迟
      this.metrics.latency = this.performanceBuffer.reduce((a, b) => a + b, 0) / this.performanceBuffer.length
    }

    // 计算消息速率
    this.calculateMessageRate()
  }

  /**
   * 记录错误
   */
  recordError(error?: Error): void {
    const now = Date.now()

    // 更新断路器状态
    this.circuitBreaker.failureCount++
    this.circuitBreaker.lastFailureTime = now

    // 检查是否需要打开断路器
    if (this.circuitBreaker.failureCount >= this.config.circuitBreaker.failureThreshold) {
      this.circuitBreaker.isOpen = true
      this.circuitBreaker.nextRetryTime = now + this.config.circuitBreaker.recoveryTimeout
    }

    // 记录错误到缓冲区
    this.errorBuffer.push(now)
    if (this.errorBuffer.length > 100) {
      this.errorBuffer.shift()
    }

    // 计算错误率
    this.calculateErrorRate()
  }

  /**
   * 检查连接是否健康
   */
  isHealthy(): boolean {
    const now = Date.now()

    // 检查断路器状态
    if (this.circuitBreaker.isOpen) {
      if (now < this.circuitBreaker.nextRetryTime) {
        return false
      } else {
        // 尝试半开状态
        this.circuitBreaker.isOpen = false
        this.circuitBreaker.failureCount = Math.max(0, this.circuitBreaker.failureCount - 1)
      }
    }

    // 检查各项健康指标
    const checks = [
      this.metrics.latency <= this.config.health.maxLatency,
      this.metrics.errorRate <= this.config.health.maxErrorRate,
      this.metrics.messageRate >= this.config.health.minMessageRate,
      (now - this.metrics.lastActivity) < this.config.circuitBreaker.monitoringWindow
    ]

    return checks.every(check => check)
  }

  /**
   * 获取健康状态
   */
  getHealthStatus(): {
    isHealthy: boolean
    metrics: HealthMetrics
    circuitBreaker: CircuitBreakerState
    issues: string[]
  } {
    const now = Date.now()
    const issues: string[] = []

    // 检查各项指标
    if (this.metrics.latency > this.config.health.maxLatency) {
      issues.push(`延迟过高: ${this.metrics.latency.toFixed(2)}ms`)
    }

    if (this.metrics.errorRate > this.config.health.maxErrorRate) {
      issues.push(`错误率过高: ${(this.metrics.errorRate * 100).toFixed(1)}%`)
    }

    if (this.metrics.messageRate < this.config.health.minMessageRate) {
      issues.push(`消息速率过低: ${this.metrics.messageRate.toFixed(2)}/min`)
    }

    if (now - this.metrics.lastActivity > this.config.circuitBreaker.monitoringWindow) {
      issues.push(`长时间无活动: ${((now - this.metrics.lastActivity) / 1000).toFixed(1)}秒`)
    }

    if (this.circuitBreaker.isOpen) {
      issues.push('断路器已打开')
    }

    return {
      isHealthy: this.isHealthy(),
      metrics: { ...this.metrics },
      circuitBreaker: { ...this.circuitBreaker },
      issues
    }
  }

  /**
   * 检查是否可以发送消息
   */
  canSendMessage(): boolean {
    // 检查断路器
    if (this.circuitBreaker.isOpen) {
      return false
    }

    // 检查背压
    if (this.config.backpressure &&
        this.messageBuffer.length >= this.config.backpressure.maxQueueSize) {
      return false
    }

    return true
  }

  /**
   * 添加消息到缓冲区
   */
  bufferMessage(message: any): boolean {
    if (!this.canSendMessage()) {
      return false
    }

    this.messageBuffer.push(message)
    return true
  }

  /**
   * 获取并清空消息缓冲区
   */
  flushMessageBuffer(): any[] {
    const messages = [...this.messageBuffer]
    this.messageBuffer = []
    return messages
  }

  /**
   * 重置断路器
   */
  resetCircuitBreaker(): void {
    this.circuitBreaker = {
      isOpen: false,
      failureCount: 0,
      lastFailureTime: 0,
      nextRetryTime: 0
    }
  }

  /**
   * 计算消息速率
   */
  private calculateMessageRate(): void {
    const now = Date.now()
    const window = 60000 // 1分钟

    // 清理过期的错误记录
    this.errorBuffer = this.errorBuffer.filter(time => now - time < window)

    // 估算消息速率（基于错误率的反向计算）
    if (this.errorBuffer.length > 0) {
      this.metrics.messageRate = Math.max(0.1, this.errorBuffer.length / (this.metrics.errorRate || 0.01))
    }
  }

  /**
   * 计算错误率
   */
  private calculateErrorRate(): void {
    const now = Date.now()
    const window = 60000 // 1分钟

    // 计算窗口内的错误数量
    const recentErrors = this.errorBuffer.filter(time => now - time < window)

    // 估算总消息数（简化计算）
    const estimatedTotalMessages = Math.max(1, recentErrors.length / 0.05) // 假设5%错误率

    this.metrics.errorRate = recentErrors.length / estimatedTotalMessages
  }

  /**
   * 启动监控循环
   */
  private startMonitoring(): void {
    setInterval(() => {
      this.updateMetrics()
    }, 10000) // 每10秒更新一次指标
  }

  /**
   * 更新指标
   */
  private updateMetrics(): void {
    const now = Date.now()

    // 更新运行时间
    this.metrics.uptime = now - (this.metrics.uptime || now)

    // 清理过期的缓冲区数据
    this.cleanupBuffers()
  }

  /**
   * 清理缓冲区
   */
  private cleanupBuffers(): void {
    const now = Date.now()
    const window = 300000 // 5分钟

    // 清理过期的性能数据
    this.performanceBuffer = this.performanceBuffer.filter((_, index) => {
      // 保留最近100个数据点或5分钟内的数据
      return index < 100 || (now - index * 1000) < window
    })

    // 清理过期的错误记录
    this.errorBuffer = this.errorBuffer.filter(time => now - time < window)
  }

  /**
   * 获取性能统计
   */
  getPerformanceStats(): any {
    return {
      metrics: this.metrics,
      circuitBreaker: this.circuitBreaker,
      bufferSize: this.messageBuffer.length,
      performanceBufferSize: this.performanceBuffer.length,
      errorBufferSize: this.errorBuffer.length,
      config: this.config
    }
  }
}

// 创建默认的健康监控实例
export const createHealthMonitor = (options?: any): ConnectionHealthMonitor => {
  return new ConnectionHealthMonitor(options)
}
