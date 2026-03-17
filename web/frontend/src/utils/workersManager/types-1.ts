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

export {
  WorkerMessageType,
  MessagePriority,
  WorkerMessageUtils
} from '@/workers/protocol.ts'

export type {
  WorkerMessage,
  WorkerResponse,
  WorkerProgress,
  WorkerError,
  WorkerConfig
} from '@/workers/protocol.ts'

export interface TechnicalIndicatorResult {
  indicator: string
  symbol: string
  data: unknown[]
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
