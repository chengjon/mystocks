import { readonly, ref } from "vue";

import { StrategyAdapter } from "@/api/adapters/strategyAdapter";
import { StrategyApiService } from "@/api/services/strategyService";
import type { BacktestRequestVM } from "@/api/types/extensions";
import {
  extractBacktestTaskId,
  extractBacktestTaskMessage,
  extractBacktestTaskStatus,
  isBacktestTerminalStatus,
  toBacktestStatusMessage,
} from "@/composables/strategy/backtestContract";
import type { StrategyBacktestTaskStatus } from "@/composables/strategy/useStrategyCrossTabContext";

export interface UseBacktestStartParams {
  startDate: string;
  endDate: string;
  initialCapital: number;
  symbols?: string[];
}

export interface BacktestTaskState {
  taskId: string;
  status: StrategyBacktestTaskStatus;
  message: string;
  progress: number;
  result?: unknown;
}

interface PollBacktestStatusOptions {
  onUpdate?: (task: BacktestTaskState) => void;
  intervalMs?: number;
  maxAttempts?: number;
}

function createBacktestPayload(strategyId: string, params: UseBacktestStartParams): BacktestRequestVM {
  return {
    strategy_id: strategyId,
    symbol: params.symbols?.[0] || "ALL",
    start_date: params.startDate,
    end_date: params.endDate,
    initial_capital: params.initialCapital,
    parameters: {},
    symbols: params.symbols,
  };
}

function resolveProgress(status: StrategyBacktestTaskStatus, reportedProgress?: number): number {
  if (typeof reportedProgress === "number" && Number.isFinite(reportedProgress)) {
    return Math.max(0, Math.min(100, Math.round(reportedProgress)));
  }

  if (status === "queued") {
    return 15;
  }
  if (status === "running") {
    return 60;
  }
  if (status === "completed") {
    return 100;
  }
  return 0;
}

function toBacktestTaskState(payload: unknown): BacktestTaskState | null {
  const taskId = extractBacktestTaskId(payload);
  const status = extractBacktestTaskStatus(payload);
  if (!taskId || !status) {
    return null;
  }

  const adaptedTask = StrategyAdapter.adaptBacktestTask(payload as never);
  const message = extractBacktestTaskMessage(payload) || toBacktestStatusMessage(status);

  return {
    taskId,
    status,
    message,
    progress: resolveProgress(status, adaptedTask?.progress),
    result: adaptedTask?.result,
  };
}

function sleep(ms: number) {
  return new Promise((resolve) => globalThis.setTimeout(resolve, ms));
}

export function useBacktest() {
  const error = ref<string | null>(null);
  const strategyService = new StrategyApiService();

  const startBacktest = async (
    strategyId: string,
    params: UseBacktestStartParams,
  ): Promise<BacktestTaskState | null> => {
    error.value = null;

    try {
      const response = await strategyService.startBacktest(strategyId, createBacktestPayload(strategyId, params));
      const task = toBacktestTaskState(response);

      if (!task) {
        error.value = extractBacktestTaskMessage(response) || "回测接口未返回可轮询的任务信息";
        return null;
      }

      return task;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "启动回测失败";
      return null;
    }
  };

  const pollBacktestStatus = async (
    taskId: string,
    options: PollBacktestStatusOptions = {},
  ): Promise<BacktestTaskState> => {
    const intervalMs = options.intervalMs ?? 1500;
    const maxAttempts = options.maxAttempts ?? 40;

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      const response = await strategyService.getBacktestStatus(taskId);
      const task = toBacktestTaskState(response);

      if (!task) {
        const message = extractBacktestTaskMessage(response) || "回测状态返回异常";
        error.value = message;
        throw new Error(message);
      }

      options.onUpdate?.(task);

      if (isBacktestTerminalStatus(task.status)) {
        return task;
      }

      await sleep(intervalMs);
    }

    error.value = "回测状态轮询超时";
    throw new Error("回测状态轮询超时");
  };

  return {
    error: readonly(error),
    startBacktest,
    pollBacktestStatus,
  };
}
