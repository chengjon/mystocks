import type { StrategyConfig } from '@/api/types/common';
import type { StrategyListItemVM } from '@/utils/strategy-adapters';
import { createMockStrategyManagementList } from '@/mock/strategyTabsMock';

export type StrategyDataSource = 'real' | 'mock';

export function normalizeStrategyStatus(status: unknown): StrategyListItemVM['status'] {
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

export function toStrategyListItemVM(strategy: StrategyConfig, index: number): StrategyListItemVM {
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

export function extractStrategyConfigs(payload: unknown): StrategyConfig[] | null {
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

export function parseProcessTimeMs(processTime?: string): string {
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

export function createMockStrategyItems(): StrategyListItemVM[] {
  return createMockStrategyManagementList().map((item, index) => toStrategyListItemVM(item, index));
}
