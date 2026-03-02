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
import type { BacktestRequestVM } from '@/api/types/extensions/strategy';
import type { StrategyConfig } from '@/api/types/common';
import { createMockStrategyManagementList } from '@/mock/strategyTabsMock';

type StrategyDataSource = 'real' | 'mock';

function normalizeStrategyStatus(status: unknown): StrategyListItemVM['status'] {
  if (typeof status !== 'string') {
    return 'stopped';
  }

  const normalized = status.toLowerCase();
  if (normalized === 'running' || normalized === 'active' || normalized === 'enabled') {
    return 'running';
  }
  if (normalized === 'paused') {
    return 'paused';
  }
  if (normalized === 'error' || normalized === 'failed') {
    return 'error';
  }
  return 'stopped';
}

function toStrategyListItemVM(strategy: StrategyConfig, index: number): StrategyListItemVM {
  return {
    id: strategy.strategy_id != null ? String(strategy.strategy_id) : `strategy-${index + 1}`,
    code: strategy.strategy_type || '',
    name: strategy.strategy_name || `策略 ${index + 1}`,
    type: strategy.strategy_type || 'custom',
    status: normalizeStrategyStatus(strategy.status),
    lastRunTime: strategy.updated_at || '-',
    nextRunTime: '-',
    totalReturn: '-',
    sharpeRatio: '-',
    maxDrawdown: '-',
    winRate: '-',
    description: strategy.description || '',
  };
}

function extractStrategyConfigs(payload: unknown): StrategyConfig[] | null {
  if (Array.isArray(payload)) {
    return payload as StrategyConfig[];
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>;
    if (Array.isArray(candidate.strategies)) {
      return candidate.strategies as StrategyConfig[];
    }
    if (Array.isArray(candidate.items)) {
      return candidate.items as StrategyConfig[];
    }
    if (Array.isArray(candidate.data)) {
      return candidate.data as StrategyConfig[];
    }
  }

  return null;
}

function parseProcessTimeMs(processTime?: string): string {
  if (!processTime) {
    return 'N/A';
  }

  const normalized = processTime.trim().toLowerCase();
  const rawNumber = Number.parseFloat(normalized);

  if (!Number.isFinite(rawNumber)) {
    return 'N/A';
  }

  if (normalized.endsWith('ms')) {
    return rawNumber.toFixed(2);
  }
  if (normalized.endsWith('s')) {
    return (rawNumber * 1000).toFixed(2);
  }
  return rawNumber.toFixed(2);
}

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
  const dataSource = ref<StrategyDataSource>('real');
  const lastRequestId = ref<string>('N/A');
  const lastProcessTimeMs = ref<string>('N/A');

  // Service instance
  const strategyService = new StrategyApiService();

  const applyMockFallback = (errorMessage: string) => {
    strategies.value = createMockStrategyManagementList().map((item, index) =>
      toStrategyListItemVM(item, index)
    );
    dataSource.value = 'mock';
    error.value = errorMessage;
  };

  /**
   * Fetch strategy list from API
   */
  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.getStrategyList();
      lastRequestId.value = response.request_id || 'N/A';
      lastProcessTimeMs.value = parseProcessTimeMs(response.process_time);

      if (!response.success) {
        applyMockFallback(response.message || '获取策略列表失败，已回退到 MOCK 数据');
        return;
      }

      const strategyList = extractStrategyConfigs(response.data);
      if (strategyList === null) {
        applyMockFallback('策略数据格式异常，已回退到 MOCK 数据');
        return;
      }

      if (strategyList.length === 0) {
        strategies.value = [];
        dataSource.value = 'real';
        return;
      }

      strategies.value = strategyList.map((item, index) => toStrategyListItemVM(item, index));
      dataSource.value = 'real';
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      applyMockFallback(`获取策略列表失败: ${errorMsg}`);
      console.error('[useStrategy] fetchStrategies error, fallback to mock:', err);
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
      return StrategyAdapter.adaptStrategyDetail(response) as unknown as Strategy | undefined;
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
    const previousStrategies = [...strategies.value];
    const tempId = `temp-${Date.now()}`;
    const optimisticItem: StrategyListItemVM = {
      id: tempId,
      code: data.type || '',
      name: data.name || '未命名策略',
      type: data.type || 'custom',
      status: 'stopped',
      lastRunTime: new Date().toISOString(),
      nextRunTime: '-',
      totalReturn: '-',
      sharpeRatio: '-',
      maxDrawdown: '-',
      winRate: '-',
      description: data.description || '',
    };
    strategies.value = [optimisticItem, ...strategies.value];

    try {
      const response = await strategyService.createStrategy(data);

      if (response.success) {
        // Refresh list after successful creation
        await fetchStrategies();
        return true;
      } else {
        strategies.value = previousStrategies;
        error.value = response.message || '创建策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      strategies.value = previousStrategies;
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
    const index = strategies.value.findIndex((s) => s.id === id);
    const previousItem = index !== -1 ? { ...strategies.value[index] } : null;

    if (index !== -1) {
      strategies.value[index] = {
        ...strategies.value[index],
        name: data.name || strategies.value[index].name,
        description: data.description || strategies.value[index].description,
      };
    }

    try {
      const response = await strategyService.updateStrategy(id, data);

      if (response.success) {
        // Update local state with partial update
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
        if (index !== -1 && previousItem) {
          strategies.value[index] = previousItem;
        }
        error.value = response.message || '更新策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      if (index !== -1 && previousItem) {
        strategies.value[index] = previousItem;
      }
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
    const previousStrategies = [...strategies.value];
    strategies.value = strategies.value.filter((s) => s.id !== id);

    try {
      const response = await strategyService.deleteStrategy(id);

      if (response.success) {
        return true;
      } else {
        strategies.value = previousStrategies;
        error.value = response.message || '删除策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      strategies.value = previousStrategies;
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
    config?: Record<string, unknown>
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
      if (response.success) {
        const index = strategies.value.findIndex((s) => s.id === id);
        if (index !== -1) {
          strategies.value[index].status = 'paused';
        }
        return true;
      }
      error.value = response.message || '暂停策略失败';
      return false;
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
      if (response.success) {
        const index = strategies.value.findIndex((s) => s.id === id);
        if (index !== -1) {
          strategies.value[index].status = 'running';
        }
        return true;
      }
      error.value = response.message || '恢复策略失败';
      return false;
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
    dataSource: readonly(dataSource),
    lastRequestId: readonly(lastRequestId),
    lastProcessTimeMs: readonly(lastProcessTimeMs),

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
  const backtestTasks = ref<unknown[]>([]);
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
      const backtestParams: BacktestRequestVM = {
        strategy_id: strategyId,
        start_date: params.startDate,
        end_date: params.endDate,
        initial_capital: params.initialCapital,
        symbol: params.symbols?.[0] ?? '',
        parameters: {
          symbols: params.symbols ?? [],
        },
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
  ): Promise<unknown> => {
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
