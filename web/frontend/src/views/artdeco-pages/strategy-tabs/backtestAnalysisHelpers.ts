import type { BacktestRequestVM } from '@/api/types/extensions'
import type { StrategyConfig } from '@/api/types/common'
import type { StrategyBacktestTaskStatus } from '@/composables/strategy/useStrategyCrossTabContext'
import type { BacktestWorkbenchDataConfig } from '@/mock/backtestWorkbenchMock'

export interface BacktestFormState {
  strategy: string
  period: string
  capital: string
  benchmark: string
}

export type BacktestTaskRowStatusClass = 'running' | 'queued' | 'done' | 'failed'

export interface BacktestTaskRow {
  name: string
  detail: string
  status: string
  statusClass: BacktestTaskRowStatusClass
}

export interface BacktestSelectOption {
  label: string
  value: string
}

export interface BacktestTableColumn {
  key: string
  label: string
}

export interface CreateBacktestPayloadInput {
  strategyId: string
  period: string
  capital: string
  benchmark: string
  optimizationParameters?: Record<string, unknown> | null
  now?: Date
}

export const optimizeColumns: BacktestTableColumn[] = [
  { key: 'name', label: '参数组' },
  { key: 'score', label: '评分' },
  { key: 'annual', label: '年化' },
  { key: 'drawdown', label: '回撤' }
]

export const reportColumns: BacktestTableColumn[] = [
  { key: 'name', label: '报告名称' },
  { key: 'period', label: '区间' },
  { key: 'return', label: '收益率' },
  { key: 'drawdown', label: '最大回撤' },
  { key: 'updatedAt', label: '生成时间' }
]

export function createDefaultBacktestConfig(source: BacktestWorkbenchDataConfig): BacktestFormState {
  return {
    strategy: source.strategyOptions[0]?.value ?? 'momentum',
    period: source.periodOptions[1]?.value ?? source.periodOptions[0]?.value ?? '1y',
    capital: '1000000',
    benchmark: source.benchmarkOptions[0]?.value ?? 'csi300'
  }
}

export function extractStrategiesFromPayload(payload: unknown): StrategyConfig[] {
  if (Array.isArray(payload)) {
    return payload as StrategyConfig[]
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>
    const collections = [candidate.strategies, candidate.items, candidate.data, candidate.records]
    for (const collection of collections) {
      if (Array.isArray(collection)) {
        return collection as StrategyConfig[]
      }
    }
  }

  return []
}

export function toBacktestTaskStatusClass(status: StrategyBacktestTaskStatus): BacktestTaskRowStatusClass {
  if (status === 'queued') {
    return 'queued'
  }
  if (status === 'running') {
    return 'running'
  }
  if (status === 'completed') {
    return 'done'
  }
  return 'failed'
}

export function toBacktestTaskStatusLabel(status: StrategyBacktestTaskStatus): string {
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

function formatBacktestDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

export function resolveBacktestDateRange(period: string, now: Date = new Date()) {
  const endDate = new Date(now)
  const startDate = new Date(endDate)
  const normalizedPeriod = period.trim().toLowerCase()

  if (normalizedPeriod.endsWith('m')) {
    const monthOffset = Number.parseInt(normalizedPeriod, 10)
    startDate.setMonth(startDate.getMonth() - (Number.isFinite(monthOffset) ? monthOffset : 12))
  } else if (normalizedPeriod.endsWith('y')) {
    const yearOffset = Number.parseInt(normalizedPeriod, 10)
    startDate.setFullYear(startDate.getFullYear() - (Number.isFinite(yearOffset) ? yearOffset : 1))
  } else {
    startDate.setFullYear(startDate.getFullYear() - 1)
  }

  return {
    startDate: formatBacktestDate(startDate),
    endDate: formatBacktestDate(endDate)
  }
}

export function normalizeInitialCapital(raw: string): number {
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return 1_000_000
  }
  return parsed
}

export function createBacktestPayload(input: CreateBacktestPayloadInput): BacktestRequestVM {
  const { startDate, endDate } = resolveBacktestDateRange(input.period, input.now)

  return {
    strategy_id: input.strategyId,
    symbol: 'ALL',
    start_date: startDate,
    end_date: endDate,
    initial_capital: normalizeInitialCapital(input.capital),
    parameters: {
      benchmark: input.benchmark,
      period: input.period,
      ...(input.optimizationParameters
        ? {
            optimization_parameters: input.optimizationParameters
          }
        : {})
    }
  }
}

export function resolveBacktestTargetStrategyId(
  selectedStrategyId: string | null | undefined,
  configuredStrategy: string | null | undefined
): string | null {
  if (selectedStrategyId) {
    return selectedStrategyId
  }

  if (configuredStrategy && typeof configuredStrategy === 'string') {
    return configuredStrategy
  }

  return null
}

export function upsertBacktestTaskRows(
  rows: BacktestTaskRow[],
  nextRow: {
    strategyId: string
    strategyName?: string | null
    status: StrategyBacktestTaskStatus
    message: string
    taskId?: string
  }
): BacktestTaskRow[] {
  const strategyName = nextRow.strategyName || `策略 ${nextRow.strategyId}`
  const detailParts = [nextRow.message]

  if (nextRow.taskId) {
    detailParts.unshift(`TASK ${nextRow.taskId}`)
  }

  const row: BacktestTaskRow = {
    name: strategyName,
    detail: detailParts.filter(Boolean).join(' · '),
    status: toBacktestTaskStatusLabel(nextRow.status),
    statusClass: toBacktestTaskStatusClass(nextRow.status)
  }

  const index = rows.findIndex((item) => item.name === strategyName)
  if (index === -1) {
    return [row, ...rows].slice(0, 10)
  }

  const cloned = [...rows]
  cloned[index] = row
  return cloned
}

export function syncStrategyOptionsWithContext(
  options: BacktestSelectOption[],
  strategyId: string | null | undefined,
  contextLabel: string
): BacktestSelectOption[] {
  if (!strategyId) {
    return options
  }

  const hasOption = options.some((option) => option.value === strategyId)
  if (!hasOption) {
    return [
      { label: contextLabel, value: strategyId },
      ...options
    ]
  }

  return options.map((option) => {
    if (option.value !== strategyId) {
      return option
    }

    return {
      ...option,
      label: contextLabel
    }
  })
}
