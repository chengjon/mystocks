/**
 * Strategy Adapter
 *
 * Handles data transformation between API responses and frontend models.
 * Implements fallback to mock data on API failures.
 */

import type { UnifiedResponse } from '../types/common';
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
      return mockStrategyList.strategies as unknown as Strategy[];
    }

    try {
      return (apiResponse.data.strategies || []).map((s: unknown) => this.adaptStrategy(s));
    } catch (error) {
      console.error('[StrategyAdapter] Failed to adapt strategy list:', error);
      return mockStrategyList.strategies as unknown as Strategy[];
    }
  }

  /**
   * Adapt single strategy from API response
   *
   * @param apiStrategy - Raw strategy object from API
   * @returns Adapted Strategy object
   */
  static adaptStrategy(apiStrategy: unknown): Strategy {
    const strategy = apiStrategy as Partial<Strategy> & {
      type?: string;
      status?: string;
      created_at?: string | Date;
      updated_at?: string | Date;
      performance?: unknown;
    };

    return {
      id: strategy.id || '',
      name: strategy.name || 'Unnamed Strategy',
      description: strategy.description || '',
      type: this.translateType(strategy.type || ''),
      status: this.translateStatus(strategy.status || ''),
      created_at: this.parseDateToString(strategy.created_at || ''),
      updated_at: this.parseDateToString(strategy.updated_at || ''),
      parameters: strategy.parameters || {},
      performance: strategy.performance
        ? this.adaptPerformance(strategy.performance)
        : undefined,
    };
  }

  /**
   * Adapt performance metrics
   *
   * @param apiPerf - Raw performance object from API
   * @returns Adapted StrategyPerformance object
   */
  static adaptPerformance(apiPerf: unknown): StrategyPerformance {
    const perf = apiPerf as {
      total_return?: number;
      totalReturn?: number;
      annualized_return?: number;
      annual_return?: number;
      annualReturn?: number;
      sharpe_ratio?: number;
      sharpeRatio?: number;
      sortino_ratio?: number;
      sortinoRatio?: number;
      max_drawdown?: number;
      maxDrawdown?: number;
      volatility?: number;
      value_at_risk?: number;
      valueAtRisk?: number;
      total_trades?: number;
      totalTrades?: number;
      win_rate?: number;
      winRate?: number;
      profit_factor?: number;
      profitLossRatio?: number;
      average_win?: number;
      averageWin?: number;
      average_loss?: number;
      averageLoss?: number;
      calmar_ratio?: number;
      calmarRatio?: number;
      information_ratio?: number;
      informationRatio?: number;
    };

    return {
      total_return: perf.total_return || perf.totalReturn || 0,
      annualized_return: perf.annualized_return || perf.annual_return || perf.annualReturn || 0,
      sharpe_ratio: perf.sharpe_ratio || perf.sharpeRatio || 0,
      sortino_ratio: perf.sortino_ratio || perf.sortinoRatio || 0,
      max_drawdown: perf.max_drawdown || perf.maxDrawdown || 0,
      volatility: perf.volatility || 0,
      value_at_risk: perf.value_at_risk || perf.valueAtRisk || 0,
      total_trades: perf.total_trades || perf.totalTrades || 0,
      win_rate: perf.win_rate || perf.winRate || 0,
      profit_factor: perf.profit_factor || perf.profitLossRatio || 0,
      average_win: perf.average_win || perf.averageWin || 0,
      average_loss: perf.average_loss || perf.averageLoss || 0,
      calmar_ratio: perf.calmar_ratio || perf.calmarRatio || 0,
      information_ratio: perf.information_ratio || perf.informationRatio || 0,
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
      const task = apiResponse.data as Partial<BacktestTask> & {
        strategyId?: string;
        task_id?: string;
        id?: string;
        startDate?: string;
        endDate?: string;
        initialCapital?: number;
        createdAt?: string | Date;
        started_at?: string | Date;
        startTime?: string | Date;
        result?: unknown;
      }; // Support both snake_case and camelCase
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
  static adaptBacktestResult(apiResult: unknown): BacktestResultVM {
    const result = apiResult as Omit<Partial<BacktestResultVM>, 'trades'> & {
      task_id?: string;
      summary?: Record<string, unknown>;
      performance?: Record<string, unknown>;
      trades?: Array<{
        trade_id?: string;
        symbol?: string;
        side?: 'buy' | 'sell';
        quantity?: number;
        price?: number;
        timestamp?: string;
        commission?: number;
        pnl?: number;
        entry_date?: string;
        entryDate?: string;
        exit_date?: string;
        exitDate?: string;
        entry_price?: number;
        entryPrice?: number;
        exit_price?: number;
        exitPrice?: number;
      }>;
      totalReturn?: number;
      equityCurve?: unknown[];
    };

    // BacktestResultVM is aliased to BacktestRequestVM, so return a valid BacktestRequestVM object
    // plus additional fields that the UI might need
    return {
      strategy_id: result.strategy_id || result.task_id || '',
      symbol: result.symbol || '',
      start_date: result.start_date || '',
      end_date: result.end_date || '',
      initial_capital: result.initial_capital || 0,
      parameters: result.parameters || {},
      // Additional fields for UI display (not in the original interface)
      status: result.status || 'completed',
      performance: this.adaptPerformance(result.summary || result.performance || {}),
      trades: (result.trades || []).map((t, index) => ({
        trade_id: t.trade_id || `trade-${index}`,
        symbol: t.symbol || '',
        side: t.side || 'buy',
        quantity: t.quantity || 0,
        price: t.price || t.entry_price || t.entryPrice || 0,
        timestamp: t.timestamp || t.entry_date || t.entryDate || t.exit_date || t.exitDate || new Date().toISOString(),
        commission: t.commission || 0,
        pnl: t.pnl || 0,
      })),
      total_return: result.total_return || result.totalReturn || 0,
      equity_curve: result.equity_curve || result.equityCurve || [],
      created_at: result.created_at || new Date().toISOString(),
      completed_at: result.completed_at || new Date().toISOString(),
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
  private static translateBacktestStatus(status: string | undefined): BacktestTask['status'] {
    const statusMap: Record<string, BacktestTask['status']> = {
      'pending': 'pending',
      'running': 'running',
      'completed': 'completed',
      'failed': 'failed',
    };

    const normalized = (status ?? '').toLowerCase();
    return statusMap[normalized] || 'pending';
  }

  /**
   * Parse date string to Date object
   *
   * @param dateStr - Date string from API
   * @returns Date object (or current date if invalid)
   */
  private static parseDate(dateStr: string | Date | undefined): Date {
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
  private static parseDateToString(dateStr: string | Date | undefined): string {
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
  static validateBacktestParams(params: unknown): params is BacktestRequest {
    const payload = params as Partial<BacktestRequest> & {
      startDate?: string;
      endDate?: string;
      initialCapital?: number;
    };

    if (!(payload.start_date || payload.startDate) || !(payload.end_date || payload.endDate)) {
      console.error('[StrategyAdapter] Missing required date parameters');
      return false;
    }

    const initialCapital = payload.initial_capital ?? payload.initialCapital;
    if (!initialCapital || initialCapital <= 0) {
      console.error('[StrategyAdapter] Invalid initial capital');
      return false;
    }

    return true;
  }
}

export default StrategyAdapter;
