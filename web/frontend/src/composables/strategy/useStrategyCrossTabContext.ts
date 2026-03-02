import { readonly, ref } from 'vue'
import type { StrategyListItemVM } from '@/utils/strategy-adapters'

export type StrategyBacktestTaskStatus = 'queued' | 'running' | 'completed' | 'failed'

export interface StrategyBacktestTaskSnapshot {
  status: StrategyBacktestTaskStatus
  taskId?: string
  message?: string
  updatedAt?: string
}

export type StrategyOptimizationWritebackTarget = 'management' | 'parameters' | 'backtest'

export interface StrategyOptimizationSnapshot {
  score: number
  recommendedParameters: Record<string, unknown>
  writebackTargets: StrategyOptimizationWritebackTarget[]
  updatedAt: string
}

export interface StrategySnapshot {
  id: string
  name: string
  type: string
  status: StrategyListItemVM['status']
  lastRunTime: string
  parameters: Record<string, unknown>
  backtest?: StrategyBacktestTaskSnapshot
  optimization?: StrategyOptimizationSnapshot
}

type StrategySnapshotMap = Record<string, StrategySnapshot>

const snapshots = ref<StrategySnapshotMap>({})
const activeStrategyId = ref<string | null>(null)

function toNormalizedId(raw: unknown): string | null {
  if (typeof raw !== 'string') {
    return null
  }

  const normalized = raw.trim()
  return normalized.length > 0 ? normalized : null
}

function createSnapshotFromListItem(
  item: StrategyListItemVM,
  existing?: StrategySnapshot
): StrategySnapshot {
  return {
    id: item.id,
    name: item.name,
    type: item.type,
    status: item.status,
    lastRunTime: item.lastRunTime,
    parameters: existing?.parameters ?? {},
    backtest: existing?.backtest,
    optimization: existing?.optimization
  }
}

function upsertSnapshot(snapshot: StrategySnapshot) {
  snapshots.value = {
    ...snapshots.value,
    [snapshot.id]: snapshot
  }
}

function upsertFromStrategyList(list: StrategyListItemVM[]) {
  const next: StrategySnapshotMap = { ...snapshots.value }

  for (const item of list) {
    if (!item.id) {
      continue
    }

    next[item.id] = createSnapshotFromListItem(item, next[item.id])
  }

  snapshots.value = next
}

function setParametersSnapshot(strategyId: string, parameters: Record<string, unknown>) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous?.name ?? normalizedId,
    type: previous?.type ?? 'custom',
    status: previous?.status ?? 'stopped',
    lastRunTime: previous?.lastRunTime ?? '-',
    parameters: { ...parameters },
    backtest: previous?.backtest,
    optimization: previous?.optimization
  }

  upsertSnapshot(next)
}

function setStatusSnapshot(strategyId: string, status: StrategyListItemVM['status']) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous?.name ?? normalizedId,
    type: previous?.type ?? 'custom',
    status,
    lastRunTime: previous?.lastRunTime ?? '-',
    parameters: previous?.parameters ?? {},
    backtest: previous?.backtest,
    optimization: previous?.optimization
  }

  upsertSnapshot(next)
}

function setBacktestTaskSnapshot(strategyId: string, payload: StrategyBacktestTaskSnapshot) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous?.name ?? normalizedId,
    type: previous?.type ?? 'custom',
    status: previous?.status ?? 'stopped',
    lastRunTime: previous?.lastRunTime ?? '-',
    parameters: previous?.parameters ?? {},
    backtest: {
      ...(previous?.backtest ?? {}),
      ...payload
    },
    optimization: previous?.optimization
  }

  upsertSnapshot(next)
}

function setOptimizationSnapshot(strategyId: string, payload: StrategyOptimizationSnapshot) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous?.name ?? normalizedId,
    type: previous?.type ?? 'custom',
    status: previous?.status ?? 'stopped',
    lastRunTime: previous?.lastRunTime ?? '-',
    parameters: previous?.parameters ?? {},
    backtest: previous?.backtest,
    optimization: {
      ...payload,
      recommendedParameters: { ...payload.recommendedParameters },
      writebackTargets: [...payload.writebackTargets]
    }
  }

  upsertSnapshot(next)
}

function clearBacktestTaskSnapshot(strategyId: string) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  if (!previous) {
    return
  }

  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous.name,
    type: previous.type,
    status: previous.status,
    lastRunTime: previous.lastRunTime,
    parameters: previous.parameters,
    optimization: previous.optimization
  }

  upsertSnapshot(next)
}

function clearOptimizationSnapshot(strategyId: string) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return
  }

  const previous = snapshots.value[normalizedId]
  if (!previous) {
    return
  }

  const next: StrategySnapshot = {
    id: normalizedId,
    name: previous.name,
    type: previous.type,
    status: previous.status,
    lastRunTime: previous.lastRunTime,
    parameters: previous.parameters,
    backtest: previous.backtest
  }

  upsertSnapshot(next)
}

function removeSnapshot(strategyId: string) {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId || !snapshots.value[normalizedId]) {
    return
  }

  const next = { ...snapshots.value }
  delete next[normalizedId]
  snapshots.value = next

  if (activeStrategyId.value === normalizedId) {
    activeStrategyId.value = null
  }
}

function setActiveStrategy(strategyId: string | null) {
  if (strategyId === null) {
    activeStrategyId.value = null
    return
  }

  activeStrategyId.value = toNormalizedId(strategyId)
}

function getSnapshot(strategyId: string): StrategySnapshot | null {
  const normalizedId = toNormalizedId(strategyId)
  if (!normalizedId) {
    return null
  }

  return snapshots.value[normalizedId] ?? null
}

function __resetStrategyCrossTabContextForTests() {
  snapshots.value = {}
  activeStrategyId.value = null
}

export function useStrategyCrossTabContext() {
  return {
    snapshots: readonly(snapshots),
    activeStrategyId: readonly(activeStrategyId),
    upsertFromStrategyList,
    setParametersSnapshot,
    setStatusSnapshot,
    setBacktestTaskSnapshot,
    clearBacktestTaskSnapshot,
    setOptimizationSnapshot,
    clearOptimizationSnapshot,
    removeSnapshot,
    setActiveStrategy,
    getSnapshot
  }
}

export { __resetStrategyCrossTabContextForTests }
