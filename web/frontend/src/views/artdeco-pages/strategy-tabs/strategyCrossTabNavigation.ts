export type StrategyCrossTabTarget = 'parameters' | 'signals' | 'backtest'

export type StrategyCrossTabRouteName = 'strategy-parameters' | 'strategy-signals' | 'strategy-backtest'

export interface StrategyCrossTabRouteLocation {
  name: StrategyCrossTabRouteName
  query: Record<string, string>
}

const TARGET_ROUTE_MAP: Record<StrategyCrossTabTarget, StrategyCrossTabRouteName> = {
  parameters: 'strategy-parameters',
  signals: 'strategy-signals',
  backtest: 'strategy-backtest'
}

function normalizeStrategyId(raw: unknown): string | null {
  if (typeof raw !== 'string') {
    return null
  }

  const normalized = raw.trim()
  return normalized.length > 0 ? normalized : null
}

export function buildStrategyCrossTabRoute(
  target: StrategyCrossTabTarget,
  strategyId: string
): StrategyCrossTabRouteLocation | null {
  const normalizedStrategyId = normalizeStrategyId(strategyId)
  if (!normalizedStrategyId) {
    return null
  }

  return {
    name: TARGET_ROUTE_MAP[target],
    query: {
      strategyId: normalizedStrategyId
    }
  }
}

export function buildQuickBacktestRoute(strategyId: string): StrategyCrossTabRouteLocation | null {
  const base = buildStrategyCrossTabRoute('backtest', strategyId)
  if (!base) {
    return null
  }

  return {
    ...base,
    query: {
      ...base.query,
      quickRun: '1'
    }
  }
}

export function extractStrategyIdFromQuery(query: Record<string, unknown>): string | null {
  const raw = query.strategyId

  if (Array.isArray(raw)) {
    return normalizeStrategyId(raw[0])
  }

  return normalizeStrategyId(raw)
}

export function extractQuickRunFlagFromQuery(query: Record<string, unknown>): boolean {
  const raw = query.quickRun
  const value = Array.isArray(raw) ? raw[0] : raw
  if (typeof value !== 'string') {
    return false
  }

  const normalized = value.trim().toLowerCase()
  return normalized === '1' || normalized === 'true'
}
