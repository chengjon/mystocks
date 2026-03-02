import type { StrategyBacktestTaskStatus } from '@/composables/strategy/useStrategyCrossTabContext'

type UnknownRecord = Record<string, unknown>

function toRecord(payload: unknown): UnknownRecord | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }
  return payload as UnknownRecord
}

function pickString(record: UnknownRecord | null, keys: string[]): string | null {
  if (!record) {
    return null
  }

  for (const key of keys) {
    const value = record[key]
    if (typeof value === 'string' && value.trim().length > 0) {
      return value.trim()
    }
  }

  return null
}

function getPayloadLayers(payload: unknown): UnknownRecord[] {
  const root = toRecord(payload)
  const nested = toRecord(root?.data)
  const result: UnknownRecord[] = []
  if (root) {
    result.push(root)
  }
  if (nested) {
    result.push(nested)
  }
  return result
}

export function extractBacktestTaskId(payload: unknown): string | null {
  const layers = getPayloadLayers(payload)
  for (const item of layers) {
    const taskId = pickString(item, ['task_id', 'taskId', 'id', 'backtest_id', 'backtestId'])
    if (taskId) {
      return taskId
    }
  }
  return null
}

export function normalizeBacktestTaskStatus(rawStatus: unknown): StrategyBacktestTaskStatus | null {
  if (typeof rawStatus !== 'string') {
    return null
  }

  const normalized = rawStatus.trim().toLowerCase()
  if (!normalized) {
    return null
  }

  if (['pending', 'queued', 'initializing', 'created', 'submitted', 'waiting'].includes(normalized)) {
    return 'queued'
  }
  if (['running', 'processing', 'executing', 'in_progress'].includes(normalized)) {
    return 'running'
  }
  if (['completed', 'success', 'succeeded', 'done', 'finished'].includes(normalized)) {
    return 'completed'
  }
  if (['failed', 'error', 'cancelled', 'canceled', 'timeout'].includes(normalized)) {
    return 'failed'
  }
  return null
}

export function extractBacktestTaskStatus(payload: unknown): StrategyBacktestTaskStatus | null {
  const layers = getPayloadLayers(payload)
  for (const item of layers) {
    const raw = item.status ?? item.state ?? item.task_status
    const normalized = normalizeBacktestTaskStatus(raw)
    if (normalized) {
      return normalized
    }
  }
  return null
}

export function extractBacktestTaskMessage(payload: unknown): string | null {
  const layers = getPayloadLayers(payload)
  for (const item of layers) {
    const message = pickString(item, ['message', 'detail', 'error', 'error_message'])
    if (message) {
      return message
    }
  }
  return null
}

export function isBacktestTerminalStatus(status: StrategyBacktestTaskStatus): boolean {
  return status === 'completed' || status === 'failed'
}

export function toBacktestStatusMessage(status: StrategyBacktestTaskStatus): string {
  if (status === 'queued') {
    return '回测任务排队中'
  }
  if (status === 'running') {
    return '回测任务执行中'
  }
  if (status === 'completed') {
    return '回测任务已完成'
  }
  return '回测任务执行失败'
}
