/**
 * Strategy API Service
 *
 * Service layer for strategy management with full UnifiedResponse support.
 * All methods return complete UnifiedResponse objects for fallback handling.
 */

import { apiGet, apiPost, apiPut, apiDelete } from '../apiClient';
import type { UnifiedResponse } from '../apiClient';
import type {
  Strategy,
  CreateStrategyRequest,
  UpdateStrategyRequest,
  BacktestParams,
  BacktestTask,
  StrategyListResponse,
} from '../types/strategy';

export class StrategyApiService {
  /**
   * 根据 APP_MODE 环境变量决定使用哪个API端点
   * - mock: 使用 /api/mock/strategy (Mock数据)
   * - real/production: 使用 /api/v1/strategy (真实API)
   */
  private readonly baseUrl: string;

  constructor() {
    // 从环境变量读取模式，默认为real
    const appMode = import.meta.env.VITE_APP_MODE || 'real';

    // 根据模式选择API端点
    if (appMode === 'mock') {
      this.baseUrl = '/api/mock/strategy';
      console.log('[Strategy API] Using Mock endpoint:', this.baseUrl);
    } else {
      this.baseUrl = '/api/v1/strategy';
      console.log('[Strategy API] Using Real endpoint:', this.baseUrl);
    }
  }

  /**
   * Get strategy list
   *
   * @param params - Query parameters (page, pageSize, status, type)
   * @returns UnifiedResponse with strategy list
   */
  async getStrategyList(params?: {
    page?: number;
    pageSize?: number;
    status?: string;
    type?: string;
  }): Promise<UnifiedResponse<StrategyListResponse>> {
    return apiGet<UnifiedResponse<StrategyListResponse>>(
      `${this.baseUrl}/strategies`  // Task 2.3.3: 使用Mock端点
    );
  }

  /**
   * Get strategy details by ID
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with strategy details
   */
  async getStrategy(id: string): Promise<UnifiedResponse<Strategy>> {
    return apiGet<UnifiedResponse<Strategy>>(`${this.baseUrl}/strategies/${id}`);
  }

  /**
   * Get strategy configuration
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with strategy configuration
   */
  async getStrategyConfig(id: string): Promise<UnifiedResponse<Strategy>> {
    return apiGet<UnifiedResponse<Strategy>>(`${this.baseUrl}/${id}/config`);
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
    return apiPost<UnifiedResponse<Strategy>>(`${this.baseUrl}/strategies`, data);
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
    return apiPut<UnifiedResponse<Strategy>>(`${this.baseUrl}/strategies/${id}`, data);
  }

  /**
   * Delete a strategy
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse (data is null for delete)
   */
  async deleteStrategy(id: string): Promise<UnifiedResponse<void>> {
    return apiDelete<UnifiedResponse<void>>(`${this.baseUrl}/strategies/${id}`);
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
    config?: Record<string, any>
  ): Promise<UnifiedResponse<any>> {
    return apiPost<UnifiedResponse<any>>(`${this.baseUrl}/${id}/start`, config);
  }

  /**
   * Stop strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with stop confirmation
   */
  async stopStrategy(id: string): Promise<UnifiedResponse<any>> {
    return apiPost<UnifiedResponse<any>>(`${this.baseUrl}/${id}/stop`);
  }

  /**
   * Pause strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with pause confirmation
   */
  async pauseStrategy(id: string): Promise<UnifiedResponse<any>> {
    return apiPost<UnifiedResponse<any>>(`${this.baseUrl}/${id}/pause`);
  }

  /**
   * Resume strategy execution
   *
   * @param id - Strategy ID
   * @returns UnifiedResponse with resume confirmation
   */
  async resumeStrategy(id: string): Promise<UnifiedResponse<any>> {
    return apiPost<UnifiedResponse<any>>(`${this.baseUrl}/${id}/resume`);
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
    return apiPost<UnifiedResponse<BacktestTask>>(
      `${this.baseUrl}/${id}/backtest`,
      params
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
      `${this.baseUrl}/backtest/${taskId}`
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
      `${this.baseUrl}/backtest/${taskId}/result`
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
      `${this.baseUrl}/${strategyId}/backtests`
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
  ): Promise<UnifiedResponse<any>> {
    return apiGet<UnifiedResponse<any>>(`${this.baseUrl}/${id}/performance`, {
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
  ): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/${id}/trades`,
      params
    );
  }

  /**
   * Get strategy templates
   *
   * @returns UnifiedResponse with templates array
   */
  async getStrategyTemplates(): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(`${this.baseUrl}/templates`);
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
    strategyData: any
  ): Promise<UnifiedResponse<Strategy>> {
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
    return apiPost<UnifiedResponse<any>>(`${this.baseUrl}/validate`, { code, type });
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
  ): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(`${this.baseUrl}/${id}/logs`, params);
  }

  /**
   * Export strategy configuration
   *
   * @param id - Strategy ID
   * @param format - Export format (json or yaml)
   * @returns Promise with Blob (file data)
   */
  async exportStrategy(id: string, format: 'json' | 'yaml' = 'json'): Promise<Blob> {
    const response = await apiGet<any>(
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
