import { ref, readonly } from 'vue';

import type { BacktestRequestVM } from '@/api/types/extensions/strategy';
import { StrategyApiService } from '@/api/services/strategyService';
import {
  extractBacktestTaskId,
  extractBacktestTaskMessage,
  extractBacktestTaskStatus,
  toBacktestStatusMessage,
} from '@/composables/strategy/backtestContract';

type BacktestTaskStatus = 'queued' | 'running' | 'completed' | 'failed';

interface BacktestTaskState {
  taskId: string;
  status: BacktestTaskStatus;
  message: string;
}

interface PollBacktestOptions {
  intervalMs?: number;
  maxAttempts?: number;
  onUpdate?: (task: BacktestTaskState) => void;
}

function normalizeStartResponse(response: unknown): BacktestTaskState | null {
  const taskId = extractBacktestTaskId(response);
  if (!taskId) {
    return null;
  }

  const status = extractBacktestTaskStatus(response) ?? 'queued';
  const message = extractBacktestTaskMessage(response) ?? toBacktestStatusMessage(status);

  return {
    taskId,
    status,
    message,
  };
}

export function useBacktest() {
  const backtestTasks = ref<BacktestTaskState[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const strategyService = new StrategyApiService();

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
      const task = normalizeStartResponse(response);

      if (task) {
        backtestTasks.value.push(task);
        return task;
      }

      error.value = '启动回测失败: 接口未返回有效 taskId';
      return null;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `启动回测失败: ${errorMsg}`;
      console.error('[useBacktest] startBacktest error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const pollBacktestStatus = async (
    taskId: string,
    intervalOrOptions: number | PollBacktestOptions = 2000
  ): Promise<BacktestTaskState> => {
    const options: PollBacktestOptions = typeof intervalOrOptions === 'number'
      ? { intervalMs: intervalOrOptions }
      : intervalOrOptions;
    const intervalMs = options.intervalMs ?? 2000;
    const maxAttempts = options.maxAttempts ?? 20;

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      try {
        const response = await strategyService.getBacktestStatus(taskId);
        const status = extractBacktestTaskStatus(response);

        if (!status) {
          throw new Error('Failed to get backtest status');
        }

        const task: BacktestTaskState = {
          taskId,
          status,
          message: extractBacktestTaskMessage(response) ?? toBacktestStatusMessage(status),
        };

        options.onUpdate?.(task);

        if (status === 'completed') {
          return task;
        }

        if (status === 'failed') {
          throw new Error(task.message || 'Backtest failed');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        error.value = `获取回测状态失败: ${errorMsg}`;
        throw err instanceof Error ? err : new Error(errorMsg);
      }

      await new Promise((resolve) => {
        setTimeout(resolve, intervalMs);
      });
    }

    const timeoutError = new Error('回测状态轮询超时');
    error.value = timeoutError.message;
    throw timeoutError;
  };

  return {
    backtestTasks: readonly(backtestTasks),
    loading: readonly(loading),
    error: readonly(error),
    startBacktest,
    pollBacktestStatus,
  };
}
