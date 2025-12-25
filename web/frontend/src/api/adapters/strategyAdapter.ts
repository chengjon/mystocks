/**
 * Strategy Adapter
 *
 * Handles data transformation between API responses and frontend models.
 * Implements fallback to mock data on API failures.
 */

import type { UnifiedResponse } from '../apiClient';
import type {
  Strategy,
  StrategyPerformance,
  BacktestTask,
  BacktestResult,
  StrategyListResponse,
} from '../types/strategy';
import { mockStrategyList, mockStrategyDetail } from '@/mock/strategyMock';

export class StrategyAdapter {
  /**
   * Adapt strategy list from API response
   *
   * @param apiResponse - Raw API response
   * @returns Array of adapted Strategy objects (falls back to mock on error)
   */
  static adaptStrategyList(
    apiResponse: UnifiedResponse<StrategyListResponse>
  ): Strategy[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[StrategyAdapter] API failed, using mock data:', apiResponse.message);
      return mockStrategyList.strategies;
    }

    try {
      return apiResponse.data.strategies.map((s) => this.adaptStrategy(s));
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt strategy list:', error);
      return mockStrategyList.strategies;
    }
  }

  /**
   * Adapt single strategy from API response
   *
   * @param apiStrategy - Raw strategy object from API
   * @returns Adapted Strategy object
   */
  static adaptStrategy(apiStrategy: any): Strategy {
    return {
      id: apiStrategy.id || '',
      name: apiStrategy.name || 'Unnamed Strategy',
      description: apiStrategy.description || '',
      type: this.translateType(apiStrategy.type),
      status: this.translateStatus(apiStrategy.status),
      createdAt: this.parseDate(apiStrategy.created_at),
      updatedAt: this.parseDate(apiStrategy.updated_at),
      parameters: apiStrategy.parameters || {},
      performance: apiStrategy.performance
        ? this.adaptPerformance(apiStrategy.performance)
        : undefined,
    };
  }

  /**
   * Adapt performance metrics
   *
   * @param apiPerf - Raw performance object from API
   * @returns Adapted StrategyPerformance object
   */
  static adaptPerformance(apiPerf: any): StrategyPerformance {
    return {
      totalReturn: apiPerf.total_return || apiPerf.totalReturn || 0,
      annualReturn: apiPerf.annual_return || apiPerf.annualReturn || 0,
      sharpeRatio: apiPerf.sharpe_ratio || apiPerf.sharpeRatio || 0,
      maxDrawdown: apiPerf.max_drawdown || apiPerf.maxDrawdown || 0,
      winRate: apiPerf.win_rate || apiPerf.winRate || 0,
      profitLossRatio: apiPerf.profit_loss_ratio || apiPerf.profitLossRatio || 0,
    };
  }

  /**
   * Adapt backtest task from API response
   *
   * @param apiResponse - Raw API response
   * @returns Adapted BacktestTask or null (on error)
   */
  static adaptBacktestTask(
    apiResponse: UnifiedResponse<BacktestTask>
  ): BacktestTask | null {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[StrategyAdapter] Backtest API failed:', apiResponse.message);
      return null;
    }

    try {
      const task = apiResponse.data;
      return {
        taskId: task.task_id || task.taskId,
        strategyId: task.strategy_id || task.strategyId,
        status: this.translateBacktestStatus(task.status),
        progress: task.progress || 0,
        startTime: this.parseDate(task.start_time),
        endTime: task.end_time ? this.parseDate(task.end_time) : undefined,
        result: task.result ? this.adaptBacktestResult(task.result) : undefined,
        error: task.error,
      };
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt backtest task:', error);
      return null;
    }
  }

  /**
   * Adapt backtest result
   *
   * @param apiResult - Raw backtest result from API
   * @returns Adapted BacktestResult object
   */
  static adaptBacktestResult(apiResult: any): BacktestResult {
    return {
      taskId: apiResult.task_id || '',
      strategyId: apiResult.strategy_id || '',
      totalReturn: apiResult.total_return || apiResult.totalReturn || 0,
      annualReturn: apiResult.annual_return || apiResult.annualReturn || 0,
      sharpeRatio: apiResult.sharpe_ratio || apiResult.sharpeRatio || 0,
      maxDrawdown: apiResult.max_drawdown || apiResult.maxDrawdown || 0,
      winRate: apiResult.win_rate || apiResult.winRate || 0,
      totalTrades: apiResult.total_trades || apiResult.totalTrades || 0,
      profitFactor: apiResult.profit_factor || apiResult.profitFactor || 0,
      equityCurve: apiResult.equity_curve || apiResult.equityCurve || [],
      trades: apiResult.trades || apiResult.trades || [],
      performanceMetrics: apiResult.performance_metrics || apiResult.performanceMetrics || {},
    };
  }

  /**
   * Adapt strategy detail from API response
   * Falls back to mock detail on error
   *
   * @param apiResponse - Raw API response
   * @returns Adapted Strategy object
   */
  static adaptStrategyDetail(
    apiResponse: UnifiedResponse<Strategy>
  ): Strategy {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[StrategyAdapter] Strategy detail API failed, using mock:', apiResponse.message);
      return mockStrategyDetail;
    }

    try {
      return this.adaptStrategy(apiResponse.data);
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt strategy detail:', error);
      return mockStrategyDetail;
    }
  }

  /**
   * Translate strategy type from API to frontend enum
   *
   * @param type - Raw type string from API
   * @returns Normalized StrategyType
   */
  private static translateType(type: string): Strategy['type'] {
    const typeMap: Record<string, Strategy['type']> = {
      'trend_following': 'trend_following',
      'trend-following': 'trend_following',
      'mean_reversion': 'mean_reversion',
      'mean-reversion': 'mean_reversion',
      'momentum': 'momentum',
    };

    const normalized = type?.toLowerCase().replace(/-/g, '_');
    return typeMap[normalized] || 'trend_following';
  }

  /**
   * Translate strategy status from API to frontend enum
   *
   * @param status - Raw status string from API
   * @returns Normalized StrategyStatus
   */
  private static translateStatus(status: string): Strategy['status'] {
    const statusMap: Record<string, Strategy['status']> = {
      'active': 'active',
      'inactive': 'inactive',
      'testing': 'testing',
    };

    const normalized = status?.toLowerCase();
    return statusMap[normalized] || 'inactive';
  }

  /**
   * Translate backtest status from API to frontend enum
   *
   * @param status - Raw status string from API
   * @returns Normalized BacktestStatus
   */
  private static translateBacktestStatus(status: string): BacktestTask['status'] {
    const statusMap: Record<string, BacktestTask['status']> = {
      'pending': 'pending',
      'running': 'running',
      'completed': 'completed',
      'failed': 'failed',
    };

    const normalized = status?.toLowerCase();
    return statusMap[normalized] || 'pending';
  }

  /**
   * Parse date string to Date object
   *
   * @param dateStr - Date string from API
   * @returns Date object (or current date if invalid)
   */
  private static parseDate(dateStr: string | Date): Date {
    if (!dateStr) {
      return new Date();
    }

    if (dateStr instanceof Date) {
      return dateStr;
    }

    try {
      return new Date(dateStr);
    } catch (error) {
      console.warn('[StrategyAdapter] Invalid date string:', dateStr);
      return new Date();
    }
  }

  /**
   * Validate strategy data
   *
   * @param strategy - Strategy object to validate
   * @returns True if valid, false otherwise
   */
  static validateStrategy(strategy: Strategy): boolean {
    if (!strategy.id || !strategy.name) {
      console.error('[StrategyAdapter] Invalid strategy: missing id or name');
      return false;
    }

    if (!['trend_following', 'mean_reversion', 'momentum'].includes(strategy.type)) {
      console.error('[StrategyAdapter] Invalid strategy type:', strategy.type);
      return false;
    }

    return true;
  }

  /**
   * Validate backtest parameters
   *
   * @param params - Backtest parameters to validate
   * @returns True if valid, false otherwise
   */
  static validateBacktestParams(params: any): params is import('../types/strategy').BacktestParams {
    if (!params.startDate || !params.endDate) {
      console.error('[StrategyAdapter] Missing required date parameters');
      return false;
    }

    if (!params.initialCapital || params.initialCapital <= 0) {
      console.error('[StrategyAdapter] Invalid initial capital');
      return false;
    }

    return true;
  }
}

export default StrategyAdapter;
