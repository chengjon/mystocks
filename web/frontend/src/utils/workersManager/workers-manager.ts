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

// Export singleton instance
export const workersManager = WorkersManager.getInstance()
