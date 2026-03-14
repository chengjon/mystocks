export interface MonitorRow {
  endpoint: string
  qps: number | string
  p95: number | string
  errorRate: string
}

interface HealthApiMetrics {
  name?: string
  endpoint?: string
  qps?: number | string
  avg_qps?: number | string
  p95?: number | string
  p95_ms?: number | string
  latency?: number | string
  avg_latency_ms?: number | string
  error_rate?: number | string
  errorRate?: number | string
}

function toPercentString(value: unknown): string {
  if (typeof value === 'string') {
    return value.includes('%') ? value : `${value}%`
  }

  if (typeof value === 'number') {
    return `${value.toFixed(2)}%`
  }

  return '0.00%'
}

function toNumberOrDash(value: unknown): number | string {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? Number(value.toFixed(2)) : '-'
  }

  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value)
    return Number.isNaN(parsed) ? value : Number(parsed.toFixed(2))
  }

  return '-'
}

function normalizeMetricsArray(payload: unknown): MonitorRow[] {
  if (!Array.isArray(payload)) {
    return []
  }

  return payload.map((item, index) => {
    const row = (item ?? {}) as HealthApiMetrics
    const endpoint = typeof row.endpoint === 'string'
      ? row.endpoint
      : typeof row.name === 'string'
        ? row.name
        : `API-${index + 1}`

    return {
      endpoint,
      qps: toNumberOrDash(row.qps ?? row.avg_qps),
      p95: toNumberOrDash(row.p95 ?? row.p95_ms ?? row.latency ?? row.avg_latency_ms),
      errorRate: toPercentString(row.errorRate ?? row.error_rate)
    }
  })
}

function normalizeDetailedHealthOutput(output: unknown): MonitorRow[] {
  if (typeof output !== 'string') {
    return []
  }

  const matches = Array.from(output.matchAll(/API端点正常:\s*([^\n\r]+)/g))
  return matches.map((match) => ({
    endpoint: match[1]?.trim() || 'API',
    qps: '-',
    p95: '-',
    errorRate: '0.00%'
  }))
}

function normalizeHealthSummary(payload: Record<string, unknown>): MonitorRow[] {
  const endpoint = typeof payload.service === 'string' ? payload.service : ''
  if (endpoint) {
    return [
      {
        endpoint,
        qps: '-',
        p95: '-',
        errorRate: '0.00%'
      }
    ]
  }

  if (typeof payload.status === 'string' && payload.status.trim()) {
    return [
      {
        endpoint: '/api/health',
        qps: '-',
        p95: '-',
        errorRate: '0.00%'
      }
    ]
  }

  return []
}

export function normalizeSystemSettingsMonitorRows(payload: unknown): MonitorRow[] {
  if (!payload || typeof payload !== 'object') {
    return []
  }

  const root = payload as Record<string, unknown>
  const data = (root.data && typeof root.data === 'object') ? root.data as Record<string, unknown> : root

  const explicitCandidates = [
    normalizeMetricsArray(data.data),
    normalizeMetricsArray(data.apis),
    normalizeMetricsArray(data.metrics),
  ]
  const explicitRows = explicitCandidates.find((rows) => rows.length > 0) ?? []

  if (explicitRows.length > 0) {
    return explicitRows
  }

  const fromDetailedOutput = normalizeDetailedHealthOutput(data.output)
  if (fromDetailedOutput.length > 0) {
    return fromDetailedOutput
  }

  return normalizeHealthSummary(data)
}
