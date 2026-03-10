/**
 * Strategy Management API Service
 *
 * Provides methods for managing trading strategies.
 */

import { request } from '@/utils/request.ts'
import { StrategyAdapter } from '@/utils/strategy-adapters.ts'
import type {
  BacktestRequest
// BacktestResponse  // Currently unused
} from '@/api/types/strategy.ts'
import type {
  StrategyListItemVM,
  StrategyConfigVM,
  BacktestResultVM
// TechnicalIndicatorVM  // Currently unused
} from '@/utils/strategy-adapters.ts'

// Type definitions for API responses
interface StrategyListResponse {
  strategies: unknown[]
  total?: number
}

interface StrategyConfigResponse {
  id: string
  name: string
  type: string
  parameters?: unknown
  [key: string]: unknown
}

interface BacktestResultResponse {
  strategy_id: string
  results: unknown
  metrics?: unknown
  [key: string]: unknown
}

class StrategyApiService {
  private baseUrl = '/api/strategy'

  /**
   * Get list of all strategies
   */
  async getStrategies(params?: {
    type?: string
    status?: string
    limit?: number
  }): Promise<StrategyListItemVM[]> {
    const rawData = await request.get(`${this.baseUrl}/list`, { params }) as StrategyListResponse[]
    return StrategyAdapter.toStrategyListVM(rawData)
  }

  /**
   * Get strategy details
   */
  async getStrategy(id: string): Promise<StrategyConfigVM> {
    const rawData = await request.get(`${this.baseUrl}/${id}`) as StrategyConfigResponse
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }

  /**
   * Get strategy configuration
   */
  async getStrategyConfig(id: string): Promise<StrategyConfigVM> {
    const rawData = await request.get(`${this.baseUrl}/${id}/config`) as StrategyConfigResponse
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }

  /**
   * Create a new strategy
   */
  async createStrategy(strategyData: {
    name: string
    description?: string
    type: string
    code?: string
    parameters?: unknown
  }): Promise<StrategyConfigVM> {
    const rawData = await request.post(`${this.baseUrl}`, strategyData) as StrategyConfigResponse
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }

  /**
   * Update strategy configuration
   */
  async updateStrategy(id: string, strategyData: unknown): Promise<StrategyConfigVM> {
    const rawData = await request.put(`${this.baseUrl}/${id}`, strategyData) as StrategyConfigResponse
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }

  /**
   * Delete a strategy
   */
  async deleteStrategy(id: string): Promise<void> {
    await request.delete(`${this.baseUrl}/${id}`)
  }

  /**
   * Start strategy execution
   */
  async startStrategy(id: string, config?: unknown): Promise<void> {
    await request.post(`${this.baseUrl}/${id}/start`, config)
  }

  /**
   * Stop strategy execution
   */
  async stopStrategy(id: string): Promise<void> {
    await request.post(`${this.baseUrl}/${id}/stop`)
  }

  /**
   * Pause strategy execution
   */
  async pauseStrategy(id: string): Promise<void> {
    await request.post(`${this.baseUrl}/${id}/pause`)
  }

  /**
   * Resume strategy execution
   */
  async resumeStrategy(id: string): Promise<void> {
    await request.post(`${this.baseUrl}/${id}/resume`)
  }

  /**
   * Run backtest
   */
  async runBacktest(backtestData: BacktestRequest): Promise<BacktestResultVM> {
    const rawData = await request.post(`${this.baseUrl}/backtest`, backtestData) as BacktestResultResponse
    return StrategyAdapter.toBacktestResultVM(rawData)
  }

  /**
   * Get backtest results
   */
  async getBacktestResults(strategyId: string): Promise<BacktestResultVM[]> {
    const rawData = await request.get(`${this.baseUrl}/${strategyId}/backtests`) as BacktestResultResponse[]
    return rawData.map((result: BacktestResultResponse) => StrategyAdapter.toBacktestResultVM(result))
  }

  /**
   * Get backtest details
   */
  async getBacktestDetails(backtestId: string): Promise<BacktestResultVM> {
    const rawData = await request.get(`/api/backtest/${backtestId}`) as BacktestResultResponse
    return StrategyAdapter.toBacktestResultVM(rawData)
  }

  /**
   * Get strategy performance summary
   */
  async getStrategyPerformance(id: string, period?: string): Promise<unknown> {
    return request.get(`${this.baseUrl}/${id}/performance`, {
      params: { period }
    })
  }

  /**
   * Get strategy trades
   */
  async getStrategyTrades(id: string, params?: {
    limit?: number
    offset?: number
    status?: string
  }): Promise<unknown> {
    return request.get(`${this.baseUrl}/${id}/trades`, { params })
  }

  /**
   * Get available strategy templates
   */
  async getStrategyTemplates(): Promise<unknown[]> {
    return request.get(`${this.baseUrl}/templates`) as unknown[]
  }

  /**
   * Clone strategy from template
   */
  async cloneFromTemplate(templateId: string, strategyData: unknown): Promise<StrategyConfigVM> {
    const rawData = await request.post(`${this.baseUrl}/clone/${templateId}`, strategyData) as StrategyConfigResponse
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }

  /**
   * Validate strategy code
   */
  async validateStrategyCode(code: string, type: string): Promise<{
    valid: boolean
    errors?: string[]
    warnings?: string[]
  }> {
    return request.post(`${this.baseUrl}/validate`, { code, type }) as Promise<{
      valid: boolean
      errors?: string[]
      warnings?: string[]
    }>
  }

  /**
   * Get strategy logs
   */
  async getStrategyLogs(id: string, params?: {
    level?: string
    limit?: number
    since?: string
  }): Promise<unknown[]> {
    return request.get(`${this.baseUrl}/${id}/logs`, { params }) as unknown[]
  }

  /**
   * Export strategy
   */
  async exportStrategy(id: string, format: 'json' | 'yaml' = 'json'): Promise<Blob> {
    const response = await request.get(`${this.baseUrl}/${id}/export`, {
      params: { format },
      responseType: 'blob'
    }) as unknown as Blob
    return response
  }

  /**
   * Import strategy
   */
  async importStrategy(file: File): Promise<StrategyConfigVM> {
    const formData = new FormData()
    formData.append('file', file)

    const rawData = await request.post(`${this.baseUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return StrategyAdapter.toStrategyConfigVM(rawData)
  }
}

// Export singleton instance
export const strategyApi = new StrategyApiService()

// Export class for dependency injection
export default StrategyApiService
