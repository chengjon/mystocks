import type { StrategyConfig } from "@/api/types/common";
import { createMockStrategyManagementList } from "@/mock/strategyTabsMock";

export function normalizeProcessTimeMs(rawValue: string): string {
  const normalized = rawValue.trim().toLowerCase();
  if (!normalized) {
    return "N/A";
  }

  const numericValue = Number.parseFloat(normalized);
  if (!Number.isFinite(numericValue)) {
    return "N/A";
  }

  if (normalized.endsWith("ms")) {
    return numericValue.toFixed(2);
  }

  if (normalized.endsWith("s")) {
    return (numericValue * 1000).toFixed(2);
  }

  return numericValue.toFixed(2);
}

export function extractStrategyConfigs(payload: unknown): StrategyConfig[] | null {
  if (Array.isArray(payload)) {
    return payload as StrategyConfig[];
  }

  if (payload && typeof payload === "object") {
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

export function createStrategyParametersMockFallback(): StrategyConfig[] {
  return createMockStrategyManagementList();
}
