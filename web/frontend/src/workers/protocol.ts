/**
 * Web Workers Communication Protocol
 * Standardized message passing between main thread and workers
 */

// Message types for different operations
export enum WorkerMessageType {
  // Control messages
  INIT = 'init',
  READY = 'ready',
  ERROR = 'error',
  PROGRESS = 'progress',
  COMPLETE = 'complete',
  TERMINATE = 'terminate',

  // Calculation messages
  CALCULATE_INDICATOR = 'calculate_indicator',
  PROCESS_KLINE_DATA = 'process_kline_data',
  CALCULATE_RISK_METRICS = 'calculate_risk_metrics',
  RUN_BACKTEST = 'run_backtest',

  // Data messages
  LOAD_DATA = 'load_data',
  SAVE_DATA = 'save_data',
  CLEAR_CACHE = 'clear_cache',

  // System messages
  HEARTBEAT = 'heartbeat',
  HEALTH_CHECK = 'health_check',
  MEMORY_USAGE = 'memory_usage'
}

// Priority levels for message processing
export enum MessagePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  URGENT = 3
}

// Standard message interface
export interface WorkerMessage {
  id: string                    // Unique message ID
  type: WorkerMessageType       // Message type
  priority: MessagePriority     // Processing priority
  timestamp: number            // Message creation time
  payload: any                 // Message data
  timeout?: number             // Optional timeout in milliseconds
  replyTo?: string             // For request-response pattern
}

// Response interface for operations
export interface WorkerResponse extends WorkerMessage {
  success: boolean
  error?: string
  duration?: number           // Processing duration in milliseconds
  result?: any               // Operation result
}

// Progress update interface
export interface WorkerProgress extends WorkerMessage {
  type: WorkerMessageType.PROGRESS
  progress: number           // 0-100 percentage
  currentStep?: string       // Current operation step
  totalSteps?: number        // Total number of steps
  eta?: number              // Estimated time remaining in milliseconds
}

// Error message interface
export interface WorkerError extends WorkerMessage {
  type: WorkerMessageType.ERROR
  error: string
  errorCode?: string
  stackTrace?: string
  recoverable: boolean       // Whether the error is recoverable
}

// Configuration for worker initialization
export interface WorkerConfig {
  maxConcurrency: number     // Maximum concurrent operations
  memoryLimit: number       // Memory limit in MB
  timeout: number           // Default timeout in milliseconds
  enableProgress: boolean   // Whether to send progress updates
  enableHeartbeat: boolean  // Whether to send heartbeat messages
  heartbeatInterval: number // Heartbeat interval in milliseconds
}

// Worker capabilities interface
export interface WorkerCapabilities {
  supportedOperations: WorkerMessageType[]
  maxMemoryUsage: number
  concurrentOperations: number
  performanceMetrics: {
    averageResponseTime: number
    operationsPerSecond: number
    memoryEfficiency: number
  }
}

// Utility functions for message handling
export class WorkerMessageUtils {
  /**
   * Create a new worker message
   */
  static createMessage(
    type: WorkerMessageType,
    payload: any,
    priority: MessagePriority = MessagePriority.NORMAL,
    timeout?: number
  ): WorkerMessage {
    return {
      id: this.generateId(),
      type,
      priority,
      timestamp: Date.now(),
      payload,
      timeout
    }
  }

  /**
   * Create a response message
   */
  static createResponse(
    originalMessage: WorkerMessage,
    success: boolean,
    result?: any,
    error?: string
  ): WorkerResponse {
    const duration = Date.now() - originalMessage.timestamp

    return {
      ...originalMessage,
      success,
      result,
      error,
      duration
    }
  }

  /**
   * Create a progress message
   */
  static createProgress(
    operationId: string,
    progress: number,
    currentStep?: string,
    totalSteps?: number,
    eta?: number
  ): WorkerProgress {
    return {
      id: this.generateId(),
      type: WorkerMessageType.PROGRESS,
      priority: MessagePriority.NORMAL,
      timestamp: Date.now(),
      payload: { operationId },
      progress,
      currentStep,
      totalSteps,
      eta
    }
  }

  /**
   * Create an error message
   */
  static createError(
    originalMessage: WorkerMessage,
    error: string,
    errorCode?: string,
    recoverable: boolean = true
  ): WorkerError {
    return {
      ...originalMessage,
      type: WorkerMessageType.ERROR,
      error,
      errorCode,
      recoverable
    }
  }

  /**
   * Generate a unique message ID
   */
  static generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Validate message structure
   */
  static validateMessage(message: any): message is WorkerMessage {
    return (
      message &&
      typeof message.id === 'string' &&
      Object.values(WorkerMessageType).includes(message.type) &&
      Object.values(MessagePriority).includes(message.priority) &&
      typeof message.timestamp === 'number' &&
      message.payload !== undefined
    )
  }

  /**
   * Check if message has expired
   */
  static isExpired(message: WorkerMessage): boolean {
    if (!message.timeout) return false
    return Date.now() - message.timestamp > message.timeout
  }

  /**
   * Get message priority weight for queuing
   */
  static getPriorityWeight(priority: MessagePriority): number {
    switch (priority) {
      case MessagePriority.LOW: return 1
      case MessagePriority.NORMAL: return 2
      case MessagePriority.HIGH: return 4
      case MessagePriority.URGENT: return 8
      default: return 1
    }
  }
}

// Message queue for managing worker communication
export class WorkerMessageQueue {
  private queue: WorkerMessage[] = []
  private maxSize = 1000

  /**
   * Add message to queue
   */
  enqueue(message: WorkerMessage): void {
    if (this.queue.length >= this.maxSize) {
      // Remove lowest priority message
      const lowestPriorityIndex = this.queue.reduce((minIndex, msg, index) => {
        const minPriority = WorkerMessageUtils.getPriorityWeight(this.queue[minIndex].priority)
        const currentPriority = WorkerMessageUtils.getPriorityWeight(msg.priority)
        return currentPriority < minPriority ? index : minIndex
      }, 0)

      this.queue.splice(lowestPriorityIndex, 1)
    }

    // Insert message in priority order (higher priority first)
    const insertIndex = this.queue.findIndex(msg =>
      WorkerMessageUtils.getPriorityWeight(msg.priority) <
      WorkerMessageUtils.getPriorityWeight(message.priority)
    )

    if (insertIndex === -1) {
      this.queue.push(message)
    } else {
      this.queue.splice(insertIndex, 0, message)
    }
  }

  /**
   * Remove and return next message
   */
  dequeue(): WorkerMessage | undefined {
    return this.queue.shift()
  }

  /**
   * Peek at next message without removing
   */
  peek(): WorkerMessage | undefined {
    return this.queue[0]
  }

  /**
   * Get queue size
   */
  size(): number {
    return this.queue.length
  }

  /**
   * Check if queue is empty
   */
  isEmpty(): boolean {
    return this.queue.length === 0
  }

  /**
   * Clear all messages
   */
  clear(): void {
    this.queue = []
  }

  /**
   * Remove expired messages
   */
  removeExpired(): number {
    const initialSize = this.queue.length
    this.queue = this.queue.filter(msg => !WorkerMessageUtils.isExpired(msg))
    return initialSize - this.queue.length
  }

  /**
   * Get messages by priority
   */
  getByPriority(priority: MessagePriority): WorkerMessage[] {
    return this.queue.filter(msg => msg.priority === priority)
  }
}

// Export default configuration
export const DEFAULT_WORKER_CONFIG: WorkerConfig = {
  maxConcurrency: 2,
  memoryLimit: 50, // MB
  timeout: 30000, // 30 seconds
  enableProgress: true,
  enableHeartbeat: true,
  heartbeatInterval: 5000 // 5 seconds
}