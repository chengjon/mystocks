/**
 * Strategy API Service
 *
 * Service layer for strategy management with full UnifiedResponse support.
 * All methods return complete UnifiedResponse objects for explicit state handling.
 */

import { apiGet, apiPost, apiPut, apiDelete } from '../apiClient.ts';
import type { UnifiedResponse } from '../types/common.ts';
import type {
  StrategyVM as Strategy,
  CreateStrategyRequestVM as CreateStrategyRequest,
  UpdateStrategyRequestVM as UpdateStrategyRequest,
  BacktestRequestVM as BacktestParams,
  BacktestRequestVM as BacktestTask,
  StrategyListResponseVM as StrategyListResponse,
} from '../types/extensions/index.ts';

type StrategyApiDataSource = 'real' | 'mock';

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object';
}

export class StrategyApiService {
  /**
   * Use the real endpoint family as the service truth.
   * Mock-vs-real routing is handled only by the shared apiClient via VITE_USE_MOCK_DATA.
   */
  private readonly baseUrl: string;
  private readonly dataSource: StrategyApiDataSource;

  constructor() {
    this.baseUrl = '/v1/strategy';
    this.dataSource = import.meta.env.VITE_USE_MOCK_DATA ? 'mock' : 'real';
  }

  getDataSource(): StrategyApiDataSource {
    return this.dataSource;
  }

  private normalizeResponse<T>(
    payload: unknown,
    fallbackMessage: string
  ): UnifiedResponse<T> {
    if (isRecord(payload) && typeof payload.success === 'boolean' && 'data' in payload) {
      return payload as unknown as UnifiedResponse<T>;
    }

    const rawPayload = isRecord(payload) ? payload : {};

    return {
      success: true,
      code: 200,
      message:
        typeof rawPayload.message === 'string' && rawPayload.message.trim().length > 0
          ? rawPayload.message
          : fallbackMessage,
      data: (('data' in rawPayload ? rawPayload.data : payload) as T),
      timestamp:
        typeof rawPayload.timestamp === 'string' && rawPayload.timestamp.trim().length > 0
          ? rawPayload.timestamp
          : new Date().toISOString(),
      request_id: typeof rawPayload.request_id === 'string' ? rawPayload.request_id : '',
      process_time: typeof rawPayload.process_time === 'string' ? rawPayload.process_time : undefined,
      errors: null
    };
  }

  /**
   * Get strategy list
   *
   * @param params - Query parameters supported by `/api/v1/strategy/strategies`
   * @returns UnifiedResponse with strategy list
   */
  async getStrategyList(params?: {
    page?: number;
    pageSize?: number;
    status?: string;
  }): Promise<UnifiedResponse<StrategyListResponse>> {
    const queryParams: Record<string, number | string> = {};

    if (typeof params?.page === 'number') {
      queryParams.page = params.page;
    }
    if (typeof params?.pageSize === 'number') {
      queryParams.page_size = params.pageSize;
    }
    if (typeof params?.status === 'string' && params.status.trim().length > 0) {
      queryParams.status = params.status;
    }

    const response = await apiGet<unknown>(
      `${this.baseUrl}/strategies`,
      Object.keys(queryParams).length > 0 ? queryParams : undefined
    );

    return this.normalizeResponse<StrategyListResponse>(response, 'ok');
  }

  /**
   * Get strategy details by ID
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with strategy details
   */
  async getStrategy(id: string): Promise<UnifiedResponse<Strategy>> {
    const response = await apiGet<unknown>(`${this.baseUrl}/strategies/${id}`);
    return this.normalizeResponse<Strategy>(response, 'ok');
  }

  /**
   * Get strategy configuration
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with strategy configuration
   */
  async getStrategyConfig(id: string): Promise<UnifiedResponse<Strategy>> {
    const response = await apiGet<unknown>(`${this.baseUrl}/${id}/config`);
    return this.normalizeResponse<Strategy>(response, 'ok');
  }

  /**
   * Create a new strategy
   *
   * @param data - Strategy creation data
   * @returns UnifiedResponse with created strategy
   */
  async createStrategy(
    data: CreateStrategyRequest
  ): Promise<UnifiedResponse<Strategy>> {
    const response = await apiPost<unknown>(`${this.baseUrl}/strategies`, data);
    return this.normalizeResponse<Strategy>(response, '策略创建成功');
  }

  /**
   * Update existing strategy
   *
   * @param id - Strategy ID
   * @param data - Strategy update data
   * @returns UnifiedResponse with updated strategy
   */
  async updateStrategy(
    id: string,
    data: UpdateStrategyRequest
  ): Promise<UnifiedResponse<Strategy>> {
    const response = await apiPut<unknown>(`${this.baseUrl}/strategies/${id}`, data);
    return this.normalizeResponse<Strategy>(response, '策略更新成功');
  }

  /**
   * Delete a strategy
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse (data is null for delete)
   */
  async deleteStrategy(id: string): Promise<UnifiedResponse<void>> {
    const response = await apiDelete<unknown>(`${this.baseUrl}/strategies/${id}`);
    return this.normalizeResponse<void>(response, '策略已归档');
  }

  /**
   * Start strategy execution
   *
   * @param id - Strategy ID
   * @param config - Optional runtime configuration
   * @returns UnifiedResponse with start confirmation
   */
  async startStrategy(
    id: string,
    config?: Record<string, unknown>
  ): Promise<UnifiedResponse<unknown>> {
    const response = await apiPost<unknown>(`${this.baseUrl}/${id}/start`, config);
    return this.normalizeResponse<unknown>(response, '策略启动成功');
  }

  /**
   * Stop strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with stop confirmation
   */
  async stopStrategy(id: string): Promise<UnifiedResponse<unknown>> {
    const response = await apiPost<unknown>(`${this.baseUrl}/${id}/stop`);
    return this.normalizeResponse<unknown>(response, '策略停止成功');
  }

  /**
   * Pause strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with pause confirmation
   */
  async pauseStrategy(id: string): Promise<UnifiedResponse<unknown>> {
    const response = await apiPost<unknown>(`${this.baseUrl}/${id}/pause`);
    return this.normalizeResponse<unknown>(response, '策略暂停成功');
  }

  /**
   * Resume strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with resume confirmation
   */
  async resumeStrategy(id: string): Promise<UnifiedResponse<unknown>> {
    const response = await apiPost<unknown>(`${this.baseUrl}/${id}/resume`);
    return this.normalizeResponse<unknown>(response, '策略恢复成功');
  }

  /**
   * Start backtest for a strategy
   *
   * @param id - Strategy ID
   * @param params - Backtest parameters
   * @returns UnifiedResponse with backtest task
   */
  async startBacktest(
    id: string,
    params: BacktestParams
  ): Promise<UnifiedResponse<BacktestTask>> {
    const requestPayload: BacktestParams = {
      ...params,
      strategy_id: id,
    };

    return apiPost<UnifiedResponse<BacktestTask>>(
      `${this.baseUrl}/backtest/run`,
      requestPayload
    );
  }

  /**
   * Get backtest status
   *
   * @param taskId - Backtest task ID
   * @returns UnifiedResponse with backtest task status
   */
  async getBacktestStatus(
    taskId: string
  ): Promise<UnifiedResponse<BacktestTask>> {
    return apiGet<UnifiedResponse<BacktestTask>>(
      `${this.baseUrl}/backtest/status/${taskId}`
    );
  }

  /**
   * Get backtest result
   *
   * @param taskId - Backtest task ID
   * @returns UnifiedResponse with backtest result
   */
  async getBacktestResult(
    taskId: string
  ): Promise<UnifiedResponse<BacktestTask>> {
    return apiGet<UnifiedResponse<BacktestTask>>(
      `${this.baseUrl}/backtest/results/${taskId}`
    );
  }

  /**
   * Get all backtest results for a strategy
   *
   * @param strategyId - Strategy ID
   * @returns UnifiedResponse with backtest results array
   */
  async getBacktestResults(
    strategyId: string
  ): Promise<UnifiedResponse<BacktestTask[]>> {
    return apiGet<UnifiedResponse<BacktestTask[]>>(
      `${this.baseUrl}/backtest/results`,
      { strategy_id: strategyId }
    );
  }

  /**
   * Get strategy performance metrics
   *
   * @param id - Strategy ID
   * @param period - Time period (day, week, month, year, all)
   * @returns UnifiedResponse with performance data
   */
  async getStrategyPerformance(
    id: string,
    period?: string
  ): Promise<UnifiedResponse<unknown>> {
    return apiGet<UnifiedResponse<unknown>>(`${this.baseUrl}/${id}/performance`, {
      period,
    });
  }

  /**
   * Get strategy trades
   *
   * @param id - Strategy ID
   * @param params - Query parameters (limit, offset, status)
   * @returns UnifiedResponse with trades array
   */
  async getStrategyTrades(
    id: string,
    params?: {
      limit?: number;
      offset?: number;
      status?: string;
    }
  ): Promise<UnifiedResponse<unknown[]>> {
    return apiGet<UnifiedResponse<unknown[]>>(
      `${this.baseUrl}/${id}/trades`,
      params
    );
  }

  /**
   * Get strategy templates
   *
   * @returns UnifiedResponse with templates array
   */
  async getStrategyTemplates(): Promise<UnifiedResponse<unknown[]>> {
    return apiGet<UnifiedResponse<unknown[]>>(`${this.baseUrl}/templates`);
  }

  /**
   * Clone strategy from template
   *
   * @param templateId - Template ID
   * @param strategyData - Strategy customization data
   * @returns UnifiedResponse with cloned strategy
   */
  async cloneFromTemplate(
    templateId: string,
    strategyData: unknown): Promise<UnifiedResponse<Strategy>> {
    return apiPost<UnifiedResponse<Strategy>>(
      `${this.baseUrl}/clone/${templateId}`,
      strategyData
    );
  }

  /**
   * Validate strategy code
   *
   * @param code - Strategy code to validate
   * @param type - Strategy type
   * @returns UnifiedResponse with validation result
   */
  async validateStrategyCode(
    code: string,
    type: string
  ): Promise<UnifiedResponse<{ valid: boolean; errors?: string[]; warnings?: string[] }>> {
    return apiPost<UnifiedResponse<{ valid: boolean; errors?: string[]; warnings?: string[] }>>(`${this.baseUrl}/validate`, { code, type });
  }

  /**
   * Get strategy logs
   *
   * @param id - Strategy ID
   * @param params - Query parameters (level, limit, since)
   * @returns UnifiedResponse with logs array
   */
  async getStrategyLogs(
    id: string,
    params?: {
      level?: string;
      limit?: number;
      since?: string;
    }
  ): Promise<UnifiedResponse<unknown[]>> {
    return apiGet<UnifiedResponse<unknown[]>>(`${this.baseUrl}/${id}/logs`, params);
  }

  /**
   * Export strategy configuration
   *
   * @param id - Strategy ID
   * @param format - Export format (json or yaml)
   * @returns Promise with Blob (file data)
   */
  async exportStrategy(id: string, format: 'json' | 'yaml' = 'json'): Promise<Blob> {
    const response = await apiGet<unknown>(
      `${this.baseUrl}/${id}/export`,
      { format }
    );

    // Convert response to Blob if it's not already
    if (response instanceof Blob) {
      return response;
    }

    // Fallback: create Blob from JSON data
    return new Blob([JSON.stringify(response, null, 2)], {
      type: format === 'json' ? 'application/json' : 'application/x-yaml',
    });
  }

  /**
   * Import strategy from file
   *
   * @param file - Strategy file to import
   * @returns UnifiedResponse with imported strategy
   */
  async importStrategy(file: File): Promise<UnifiedResponse<Strategy>> {
    const formData = new FormData();
    formData.append('file', file);

    return apiPost<UnifiedResponse<Strategy>>(`${this.baseUrl}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
}

// Export singleton instance
export const strategyApiService = new StrategyApiService();

// Export class for dependency injection
export default StrategyApiService;
