/**
 * Strategy Composable
 *
 * Vue 3 composable for strategy management with automatic error handling,
 * loading states, and Mock data fallback.
 */

import { ref, readonly, onMounted } from 'vue';
import { StrategyApiService } from '@/api/services/strategyService';
import { StrategyAdapter } from '@/utils/strategy-adapters';
import type { StrategyVM as Strategy } from '@/api/types/extensions';
import type { StrategyListItemVM } from '@/utils/strategy-adapters';
import type { CreateStrategyRequestVM as CreateStrategyRequest, UpdateStrategyRequestVM as UpdateStrategyRequest } from '@/api/types/extensions';

/**
 * Strategy management composable
 *
 * @returns Strategy management state and methods
 */
export function useStrategy(autoFetch = true) {
  // State
  const strategies = ref<StrategyListItemVM[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Service instance
  const strategyService = new StrategyApiService();

  /**
   * Fetch strategy list from API
   */
  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.getStrategyList();
      strategies.value = StrategyAdapter.adaptStrategyList(response);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取策略列表失败: ${errorMsg}`;
      console.error('[useStrategy] fetchStrategies error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get single strategy by ID
   *
   * @param id - Strategy ID
   * @returns Strategy object or undefined
   */
  const getStrategyById = async (id: string): Promise<Strategy | undefined> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.getStrategy(id);
      return StrategyAdapter.adaptStrategyDetail(response) as any;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取策略详情失败: ${errorMsg}`;
      console.error('[useStrategy] getStrategyById error:', err);
      return undefined;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Create new strategy
   *
   * @param data - Strategy creation data
   * @returns True if successful, false otherwise
   */
  const createStrategy = async (data: CreateStrategyRequest): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.createStrategy(data);

      if (response.success) {
        // Refresh list after successful creation
        await fetchStrategies();
        return true;
      } else {
        error.value = response.message || '创建策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `创建策略失败: ${errorMsg}`;
      console.error('[useStrategy] createStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Update existing strategy
   *
   * @param id - Strategy ID
   * @param data - Strategy update data
   * @returns True if successful, false otherwise
   */
  const updateStrategy = async (
    id: string,
    data: UpdateStrategyRequest
  ): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.updateStrategy(id, data);

      if (response.success) {
        // Update local state with partial update
        const index = strategies.value.findIndex((s) => s.id === id);
        if (index !== -1 && response.data) {
          // Update only the fields that exist in StrategyListItemVM
          const updated = StrategyAdapter.adaptStrategy(response.data);
          strategies.value[index] = {
            ...strategies.value[index],
            name: updated.name || strategies.value[index].name,
            description: updated.description || strategies.value[index].description,
            type: updated.type || strategies.value[index].type,
          };
        }
        return true;
      } else {
        error.value = response.message || '更新策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `更新策略失败: ${errorMsg}`;
      console.error('[useStrategy] updateStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Delete strategy
   *
   * @param id - Strategy ID
   * @returns True if successful, false otherwise
   */
  const deleteStrategy = async (id: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.deleteStrategy(id);

      if (response.success) {
        // Remove from local list
        strategies.value = strategies.value.filter((s) => s.id !== id);
        return true;
      } else {
        error.value = response.message || '删除策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `删除策略失败: ${errorMsg}`;
      console.error('[useStrategy] deleteStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Start strategy execution
   *
   * @param id - Strategy ID
   * @param config - Optional runtime configuration
   * @returns True if successful, false otherwise
   */
  const startStrategy = async (
    id: string,
    config?: Record<string, any>
  ): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.startStrategy(id, config);

      if (response.success) {
        // Update local status to running
        const index = strategies.value.findIndex((s) => s.id === id);
        if (index !== -1) {
          strategies.value[index].status = 'running';
        }
        return true;
      } else {
        error.value = response.message || '启动策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `启动策略失败: ${errorMsg}`;
      console.error('[useStrategy] startStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Stop strategy execution
   *
   * @param id - Strategy ID
   * @returns True if successful, false otherwise
   */
  const stopStrategy = async (id: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.stopStrategy(id);

      if (response.success) {
        // Update local status to stopped
        const index = strategies.value.findIndex((s) => s.id === id);
        if (index !== -1) {
          strategies.value[index].status = 'stopped';
        }
        return true;
      } else {
        error.value = response.message || '停止策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `停止策略失败: ${errorMsg}`;
      console.error('[useStrategy] stopStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Pause strategy execution
   *
   * @param id - Strategy ID
   * @returns True if successful, false otherwise
   */
  const pauseStrategy = async (id: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.pauseStrategy(id);
      return response.success;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `暂停策略失败: ${errorMsg}`;
      console.error('[useStrategy] pauseStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Resume strategy execution
   *
   * @param id - Strategy ID
   * @returns True if successful, false otherwise
   */
  const resumeStrategy = async (id: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.resumeStrategy(id);
      return response.success;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `恢复策略失败: ${errorMsg}`;
      console.error('[useStrategy] resumeStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null;
  };

  // Auto-fetch on mount
  if (autoFetch) {
    onMounted(() => {
      fetchStrategies();
    });
  }

  return {
    // State (readonly)
    strategies: readonly(strategies),
    loading: readonly(loading),
    error: readonly(error),

    // Methods
    fetchStrategies,
    getStrategyById,
    createStrategy,
    updateStrategy,
    deleteStrategy,
    startStrategy,
    stopStrategy,
    pauseStrategy,
    resumeStrategy,
    clearError,
  };
}

/**
 * Backtest management composable
 */
export function useBacktest() {
  // State
  const backtestTasks = ref<any[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Service instance
  const strategyService = new StrategyApiService();

  /**
   * Start backtest
   *
   * @param strategyId - Strategy ID
   * @param params - Backtest parameters
   * @returns Backtest task or null
   */
  const startBacktest = async (
    strategyId: string,
    params: {
      startDate: string;
      endDate: string;
      initialCapital: number;
      symbols?: string[];
    }
  ) => {
    loading.value = true;
    error.value = null;

    try {
      // Convert camelCase params to snake_case for API
      const backtestParams: any = {
        strategy_id: parseInt(strategyId, 10),
        start_date: params.startDate,
        end_date: params.endDate,
        initial_capital: params.initialCapital,
        symbols: params.symbols,
      };
      const response = await strategyService.startBacktest(strategyId, backtestParams);
      const task = StrategyAdapter.adaptBacktestTask(response);

      if (task) {
        backtestTasks.value.push(task);
        return task;
      } else {
        error.value = '启动回测失败';
        return null;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `启动回测失败: ${errorMsg}`;
      console.error('[useBacktest] startBacktest error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Poll backtest status
   *
   * @param taskId - Backtest task ID
   * @param interval - Polling interval in ms (default: 2000)
   * @returns Promise that resolves when backtest completes
   */
  const pollBacktestStatus = async (
    taskId: string,
    interval = 2000
  ): Promise<any> => {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await strategyService.getBacktestStatus(taskId);
          const task = StrategyAdapter.adaptBacktestTask(response);

          if (!task) {
            reject(new Error('Failed to get backtest status'));
            return;
          }

          if (task.status === 'completed') {
            resolve(task);
          } else if (task.status === 'failed') {
            reject(new Error(task.error || 'Backtest failed'));
          } else {
            // Continue polling
            setTimeout(poll, interval);
          }
        } catch (err) {
          reject(err);
        }
      };

      poll();
    });
  };

  return {
    backtestTasks: readonly(backtestTasks),
    loading: readonly(loading),
    error: readonly(error),
    startBacktest,
    pollBacktestStatus,
  };
}

export default useStrategy;
