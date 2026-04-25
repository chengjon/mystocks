/**
 * Strategy Composable
 *
 * Vue 3 composable for strategy management with automatic error handling
 * and loading states.
 */

import { ref, readonly, onMounted } from 'vue';
import { StrategyApiService } from '@/api/services/strategyService';
import { StrategyAdapter } from '@/utils/strategy-adapters';
import type { StrategyVM as Strategy } from '@/api/types/extensions';
import type { StrategyListItemVM } from '@/utils/strategy-adapters';
import type { CreateStrategyRequestVM as CreateStrategyRequest, UpdateStrategyRequestVM as UpdateStrategyRequest } from '@/api/types/extensions';
import { useBacktest } from './useStrategy.backtest';
import {
  extractStrategyConfigs,
  parseProcessTimeMs,
  toStrategyListItemVM,
  type StrategyDataSource
} from './useStrategy.shared';

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
  const listError = ref<string | null>(null);
  const dataSource = ref<StrategyDataSource>('real');
  const lastRequestId = ref<string>('N/A');
  const lastProcessTimeMs = ref<string>('N/A');

  // Service instance
  const strategyService = new StrategyApiService();

  const resolveDataSource = (): StrategyDataSource => strategyService.getDataSource();

  const applyListFailure = (errorMessage: string) => {
    error.value = errorMessage;
    listError.value = errorMessage;
    dataSource.value = resolveDataSource();
  };

  /**
   * Fetch strategy list from API
   */
  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;
    listError.value = null;

    try {
      const response = await strategyService.getStrategyList();
      lastRequestId.value = response.request_id || 'N/A';
      lastProcessTimeMs.value = parseProcessTimeMs(response.process_time);

      if (!response.success) {
        applyListFailure(response.message || '获取策略列表失败');
        return;
      }

      const strategyList = extractStrategyConfigs(response.data);
      if (strategyList === null) {
        applyListFailure('策略数据格式异常');
        return;
      }

      if (strategyList.length === 0) {
        strategies.value = [];
        listError.value = null;
        dataSource.value = resolveDataSource();
        return;
      }

      strategies.value = strategyList.map((item, index) => toStrategyListItemVM(item, index));
      listError.value = null;
      dataSource.value = resolveDataSource();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      applyListFailure(`获取策略列表失败: ${errorMsg}`);
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

      if (!response.success) {
        error.value = response.message || '获取策略详情失败';
        return undefined;
      }

      const strategy = StrategyAdapter.adaptStrategyDetail(response);
      if (!strategy) {
        error.value = '策略详情不可用';
      }

      return strategy as unknown as Strategy | undefined;
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
    listError.value = null;
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
    listError: readonly(listError),
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

export { useBacktest };

export default useStrategy;
