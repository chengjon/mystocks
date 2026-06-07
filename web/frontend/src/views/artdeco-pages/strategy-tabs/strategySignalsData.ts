export interface StrategySignalItem {
  symbol: string
  name: string
  type: 'BUY' | 'SELL' | 'HOLD'
  price: number
  time: string
  strategy: string
  sortTimestamp: number | null
  signalId?: string | null
  reason?: string | null
  confidence?: number | null
  strength?: string | number | null
}

type RawSignal = Partial<StrategySignalItem> & Record<string, unknown>

interface SignalPayload {
  items?: RawSignal[]
  data?: RawSignal[]
  records?: RawSignal[]
}

function normalizeSignalType(type?: unknown): StrategySignalItem['type'] {
  if (typeof type !== 'string') {
    return 'HOLD'
  }

  const normalized = type.toUpperCase()
  if (normalized === 'BUY' || normalized === 'SELL' || normalized === 'HOLD') {
    return normalized
  }

  return 'HOLD'
}

function extractRawItems(payload: unknown): RawSignal[] {
  if (Array.isArray(payload)) {
    return payload as RawSignal[]
  }

  if (!payload || typeof payload !== 'object') {
    return []
  }

  const data = payload as SignalPayload
  if (Array.isArray(data.items)) return data.items
  if (Array.isArray(data.data)) return data.data
  if (Array.isArray(data.records)) return data.records

  return []
}

function parseTimestampCandidate(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value > 1_000_000_000_000 ? value : value * 1000
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const numeric = Number(value)
    if (Number.isFinite(numeric)) {
      return numeric > 1_000_000_000_000 ? numeric : numeric * 1000
    }

    const parsed = Date.parse(value)
    return Number.isNaN(parsed) ? null : parsed
  }

  return null
}

function normalizeOptionalString(value: unknown): string | null {
  if (typeof value !== 'string') {
    return null
  }

  const normalized = value.trim()
  return normalized.length > 0 ? normalized : null
}

function normalizeOptionalNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim().length > 0) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

function resolveSignalSortTimestamp(item: RawSignal): number | null {
  const directCandidates = [
    item.timestamp,
    item.created_at,
    item.createdAt,
    item.datetime,
    item.dateTime,
    item.occurred_at,
    item.occurredAt,
  ]

  for (const candidate of directCandidates) {
    const parsed = parseTimestampCandidate(candidate)
    if (parsed !== null) {
      return parsed
    }
  }

  const dateValue = typeof item.date === 'string' ? item.date.trim() : ''
  const timeValue = typeof item.time === 'string' ? item.time.trim() : ''
  if (dateValue && timeValue) {
    const parsed = Date.parse(`${dateValue}T${timeValue}`)
    if (!Number.isNaN(parsed)) {
      return parsed
    }
  }

  return null
}

export function createStrategySignalsFromResponse(payload: unknown): StrategySignalItem[] {
  const items = extractRawItems(payload)
  if (items.length === 0) {
    return []
  }

  return items.map((item, index) => ({
    symbol: typeof item.symbol === 'string' ? item.symbol : `UNKNOWN-${index + 1}`,
    name: typeof item.name === 'string' ? item.name : '未知标的',
    type: normalizeSignalType(item.type),
    price: normalizeOptionalNumber(item.price) ?? 0,
    time: typeof item.time === 'string' ? item.time : '--:--:--',
    strategy: typeof item.strategy === 'string' ? item.strategy : 'N/A',
    sortTimestamp: resolveSignalSortTimestamp(item),
    signalId: normalizeOptionalString(item.signal_id ?? item.signalId ?? item.id),
    reason: normalizeOptionalString(item.reason),
    confidence: normalizeOptionalNumber(item.confidence),
    strength: typeof item.strength === 'string' || typeof item.strength === 'number' ? item.strength : null,
  }))
}
