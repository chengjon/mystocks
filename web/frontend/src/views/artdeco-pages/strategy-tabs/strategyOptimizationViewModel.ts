import type { StrategyConfig } from '@/api/types/common'
import type { StrategySnapshot } from '@/composables/strategy/useStrategyCrossTabContext'

export type OptimizationStatusLabel = 'RUNNING' | 'PAUSED' | 'STOPPED' | 'ERROR'
export type OptimizationDataSource = 'real' | 'mock'

export interface StrategyOptimizationRow {
  strategyId: string
  strategyName: string
  strategyType: string
  statusLabel: OptimizationStatusLabel
  parameterCount: number
  recommendedParameters: Record<string, unknown>
  backtestStatus: string
  score: number
  lastUpdated: string
  source: OptimizationDataSource
}

function normalizeId(rawId: unknown): string {
  if (typeof rawId === 'number' && Number.isFinite(rawId)) {
    return String(rawId)
  }
  if (typeof rawId === 'string' && rawId.trim().length > 0) {
    return rawId.trim()
  }
  return ''
}

function normalizeBacktestStatus(status?: StrategySnapshot['backtest'] extends infer T
  ? T extends { status: infer S }
    ? S
    : never
  : never): string {
  if (!status) {
    return 'N/A'
  }

  if (status === 'queued') {
    return 'QUEUED'
  }
  if (status === 'running') {
    return 'RUNNING'
  }
  if (status === 'completed') {
    return 'COMPLETED'
  }
  return 'FAILED'
}

function toStableScore(input: string): number {
  let hash = 0
  for (const char of input) {
    hash = (hash * 31 + char.charCodeAt(0)) % 1000
  }
  return 70 + (Math.abs(hash) % 26)
}

function resolveStrategyStatus(rawStatus: unknown): OptimizationStatusLabel {
  if (typeof rawStatus !== 'string') {
    return 'STOPPED'
  }

  const normalized = rawStatus.trim().toLowerCase()
  if (normalized === 'running' || normalized === 'active' || normalized === 'enabled') {
    return 'RUNNING'
  }
  if (normalized === 'paused' || normalized === 'testing') {
    return 'PAUSED'
  }
  if (normalized === 'error' || normalized === 'failed') {
    return 'ERROR'
  }
  return 'STOPPED'
}

export function toOptimizationStatusLabel(
  rawStatus: unknown,
  snapshotStatus?: StrategySnapshot['status']
): OptimizationStatusLabel {
  if (snapshotStatus) {
    if (snapshotStatus === 'running') return 'RUNNING'
    if (snapshotStatus === 'paused') return 'PAUSED'
    if (snapshotStatus === 'error') return 'ERROR'
    return 'STOPPED'
  }

  return resolveStrategyStatus(rawStatus)
}

function toParameterCount(strategy: StrategyConfig, snapshot?: StrategySnapshot): number {
  const snapshotCount = snapshot ? Object.keys(snapshot.parameters ?? {}).length : 0
  if (snapshotCount > 0) {
    return snapshotCount
  }
  return strategy.parameters?.length ?? 0
}

function toLastUpdated(strategy: StrategyConfig, snapshot?: StrategySnapshot): string {
  if (strategy.updated_at && String(strategy.updated_at).trim().length > 0) {
    return String(strategy.updated_at)
  }
  if (snapshot?.lastRunTime && snapshot.lastRunTime.trim().length > 0) {
    return snapshot.lastRunTime
  }
  return '-'
}

function toRecommendedParameters(strategy: StrategyConfig, snapshot?: StrategySnapshot): Record<string, unknown> {
  const snapshotParameters = snapshot?.parameters ?? {}
  if (Object.keys(snapshotParameters).length > 0) {
    return { ...snapshotParameters }
  }

  const fallbackParameters: Record<string, unknown> = {}
  for (const item of strategy.parameters ?? []) {
    const key = item.name
    if (!key) {
      continue
    }
    fallbackParameters[key] = item.value
  }

  return fallbackParameters
}

export function buildOptimizationRows(
  strategies: StrategyConfig[],
  snapshots: Record<string, StrategySnapshot>,
  source: OptimizationDataSource = 'real'
): StrategyOptimizationRow[] {
  return strategies
    .map((strategy, index) => {
      const strategyId = normalizeId(strategy.strategy_id ?? strategy.strategy_name ?? `strategy-${index + 1}`)
      if (!strategyId) {
        return null
      }

      const snapshot = snapshots[strategyId]
      const strategyName = strategy.strategy_name || snapshot?.name || `策略 ${index + 1}`
      const strategyType = strategy.strategy_type || snapshot?.type || 'custom'
      const statusLabel = toOptimizationStatusLabel(strategy.status, snapshot?.status)
      const parameterCount = toParameterCount(strategy, snapshot)
      const recommendedParameters = toRecommendedParameters(strategy, snapshot)
      const backtestStatus = normalizeBacktestStatus(snapshot?.backtest?.status)
      const score = toStableScore(
        `${strategyId}:${strategyType}:${statusLabel}:${parameterCount}:${Object.keys(recommendedParameters).join(',')}`
      )

      return {
        strategyId,
        strategyName,
        strategyType,
        statusLabel,
        parameterCount,
        recommendedParameters,
        backtestStatus,
        score,
        lastUpdated: toLastUpdated(strategy, snapshot),
        source
      }
    })
    .filter((item): item is StrategyOptimizationRow => item !== null)
}

export function createMockOptimizationRows(): StrategyOptimizationRow[] {
  return [
    {
      strategyId: 'mock-1',
      strategyName: '动量轮动优化',
      strategyType: 'momentum',
      statusLabel: 'RUNNING',
      parameterCount: 4,
      recommendedParameters: {
        lookback: 21,
        hold_days: 5,
        max_drawdown: 0.12,
        risk_budget: 0.03
      },
      backtestStatus: 'COMPLETED',
      score: 91,
      lastUpdated: '2026-03-01 09:30:00',
      source: 'mock'
    },
    {
      strategyId: 'mock-2',
      strategyName: '均值回归优化',
      strategyType: 'mean_reversion',
      statusLabel: 'PAUSED',
      parameterCount: 3,
      recommendedParameters: {
        reversion_window: 14,
        zscore_limit: 2.4,
        max_holding_days: 6
      },
      backtestStatus: 'RUNNING',
      score: 84,
      lastUpdated: '2026-03-01 09:20:00',
      source: 'mock'
    },
    {
      strategyId: 'mock-3',
      strategyName: '多因子稳健组合',
      strategyType: 'custom',
      statusLabel: 'STOPPED',
      parameterCount: 5,
      recommendedParameters: {
        factor_a: 0.35,
        factor_b: 0.25,
        factor_c: 0.4,
        rebalance_days: 3,
        risk_limit: 0.05
      },
      backtestStatus: 'N/A',
      score: 79,
      lastUpdated: '2026-03-01 09:05:00',
      source: 'mock'
    }
  ]
}
