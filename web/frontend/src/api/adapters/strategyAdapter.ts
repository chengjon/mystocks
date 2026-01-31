/**
 * Strategy Adapter
 *
 * Handles data transformation between API responses and frontend models.
 * Implements fallback to mock data on API failures.
 */

import type { UnifiedResponse } from '../apiClient';
import type {
  StrategyVM as Strategy,
  StrategyPerformanceVM as StrategyPerformance,
  BacktestRequestVM as BacktestTask,
  BacktestResultVM,
  StrategyListResponseVM as StrategyListResponse,
} from '../types/extensions';
import type { BacktestRequest } from '../types/strategy';
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
      return mockStrategyList.strategies as any;
    }

    try {
      return (apiResponse.data.strategies || []).map((s: any) => this.adaptStrategy(s));
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt strategy list:', error);
      return mockStrategyList.strategies as any;
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
      created_at: this.parseDateToString(apiStrategy.created_at),
      updated_at: this.parseDateToString(apiStrategy.updated_at),
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
      total_return: apiPerf.total_return || apiPerf.totalReturn || 0,
      annualized_return: apiPerf.annualized_return || apiPerf.annual_return || apiPerf.annualReturn || 0,
      sharpe_ratio: apiPerf.sharpe_ratio || apiPerf.sharpeRatio || 0,
      sortino_ratio: apiPerf.sortino_ratio || apiPerf.sortinoRatio || 0,
      max_drawdown: apiPerf.max_drawdown || apiPerf.maxDrawdown || 0,
      volatility: apiPerf.volatility || 0,
      value_at_risk: apiPerf.value_at_risk || apiPerf.valueAtRisk || 0,
      total_trades: apiPerf.total_trades || apiPerf.totalTrades || 0,
      win_rate: apiPerf.win_rate || apiPerf.winRate || 0,
      profit_factor: apiPerf.profit_factor || apiPerf.profitLossRatio || 0,
      average_win: apiPerf.average_win || apiPerf.averageWin || 0,
      average_loss: apiPerf.average_loss || apiPerf.averageLoss || 0,
      calmar_ratio: apiPerf.calmar_ratio || apiPerf.calmarRatio || 0,
      information_ratio: apiPerf.information_ratio || apiPerf.informationRatio || 0,
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
      const task = apiResponse.data as any; // Support both snake_case and camelCase
      return {
        strategy_id: task.strategy_id || task.strategyId || task.task_id || task.id || '',
        symbol: task.symbol || '',
        start_date: task.start_date || task.startDate || '',
        end_date: task.end_date || task.endDate || '',
        initial_capital: task.initial_capital || task.initialCapital || 0,
        parameters: task.parameters || {},
        // Additional fields not in the original interface but used by the UI
        status: this.translateBacktestStatus(task.status),
        created_at: this.parseDateToString(task.created_at || task.createdAt),
        progress: task.progress || 0,
        startTime: this.parseDateToString(task.started_at || task.startTime),
        result: task.result ? this.adaptBacktestResult(task.result) : undefined,
      } as BacktestTask;
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt backtest task:', error);
      return null;
    }
  }

  /**
   * Adapt backtest result
   *
   * @param apiResult - Raw backtest result from API
   * @returns Adapted BacktestResultVM object
   */
  static adaptBacktestResult(apiResult: any): BacktestResultVM {
    // BacktestResultVM is aliased to BacktestRequestVM, so return a valid BacktestRequestVM object
    // plus additional fields that the UI might need
    return {
      strategy_id: apiResult.strategy_id || apiResult.task_id || '',
      symbol: apiResult.symbol || '',
      start_date: apiResult.start_date || '',
      end_date: apiResult.end_date || '',
      initial_capital: apiResult.initial_capital || 0,
      parameters: apiResult.parameters || {},
      // Additional fields for UI display (not in the original interface)
      status: apiResult.status || 'completed',
      performance: apiResult.summary || apiResult.performance || {},
      trades: (apiResult.trades || []).map((t: any) => ({
        symbol: t.symbol || '',
        entry_date: t.entry_date || t.entryDate || '',
        exit_date: t.exit_date || t.exitDate || '',
        entry_price: t.entry_price || t.entryPrice || 0,
        exit_price: t.exit_price || t.exitPrice || 0,
        pnl: t.pnl || 0,
      })),
      total_return: apiResult.total_return || apiResult.totalReturn || 0,
      equity_curve: apiResult.equity_curve || apiResult.equityCurve || [],
      created_at: apiResult.created_at || new Date().toISOString(),
      completed_at: apiResult.completed_at || new Date().toISOString(),
    } as BacktestResultVM;
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
    } catch (_) {
      console.warn('[StrategyAdapter] Invalid date string:', dateStr);
      return new Date();
    }
  }

  /**
   * Parse date string to ISO string
   *
   * @param dateStr - Date string from API
   * @returns ISO date string (or current date if invalid)
   */
  private static parseDateToString(dateStr: string | Date): string {
    const date = this.parseDate(dateStr);
    return date.toISOString();
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

    if (!strategy.type || !['trend_following', 'mean_reversion', 'momentum'].includes(strategy.type)) {
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
  static validateBacktestParams(params: any): params is BacktestRequest {
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
