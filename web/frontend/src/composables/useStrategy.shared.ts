import { StrategyAdapter, type StrategyListItemVM } from "@/utils/strategy-adapters";
import {
  extractStrategyConfigs as extractStrategyConfigsFromPayload,
  normalizeProcessTimeMs,
} from "@/views/artdeco-pages/strategy-tabs/strategyParametersData";

export type StrategyDataSource = "real" | "mock";

type UnknownRecord = Record<string, unknown>;

function toRecord(value: unknown): UnknownRecord | null {
  if (!value || typeof value !== "object") {
    return null;
  }

  return value as UnknownRecord;
}

function toStatus(value: unknown): StrategyListItemVM["status"] {
  if (typeof value !== "string") {
    return "stopped";
  }

  const normalized = value.trim().toLowerCase();
  if (["active", "running", "enabled"].includes(normalized)) {
    return "running";
  }
  if (["paused"].includes(normalized)) {
    return "paused";
  }
  if (["error", "failed"].includes(normalized)) {
    return "error";
  }
  return "stopped";
}

function toTextMetric(value: unknown, fallback = "-"): string {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value.toFixed(2);
  }
  if (typeof value === "string" && value.trim().length > 0) {
    return value.trim();
  }
  return fallback;
}

export const extractStrategyConfigs = extractStrategyConfigsFromPayload;

export function parseProcessTimeMs(rawValue: unknown): string {
  if (typeof rawValue !== "string") {
    return "N/A";
  }

  return normalizeProcessTimeMs(rawValue);
}

export function toStrategyListItemVM(item: unknown, index: number): StrategyListItemVM {
  const adapted = StrategyAdapter.toStrategyListVM([item as never])[0];
  if (adapted) {
    return adapted;
  }

  const record = toRecord(item);
  const fallbackId = typeof record?.id === "string" && record.id.trim().length > 0 ? record.id : `strategy-${index + 1}`;
  const fallbackName =
    typeof record?.name === "string" && record.name.trim().length > 0 ? record.name : `策略 ${index + 1}`;
  const fallbackCode =
    typeof record?.code === "string" && record.code.trim().length > 0 ? record.code : fallbackId;

  return {
    id: fallbackId,
    code: fallbackCode,
    name: fallbackName,
    type: typeof record?.type === "string" && record.type.trim().length > 0 ? record.type : "custom",
    status: toStatus(record?.status),
    lastRunTime: typeof record?.last_run_time === "string" ? record.last_run_time : "从未运行",
    nextRunTime: typeof record?.next_run_time === "string" ? record.next_run_time : "未设置",
    totalReturn: toTextMetric(record?.total_return),
    sharpeRatio: toTextMetric(record?.sharpe_ratio),
    maxDrawdown: toTextMetric(record?.max_drawdown),
    winRate: toTextMetric(record?.win_rate),
    description: typeof record?.description === "string" ? record.description : "",
  };
}
