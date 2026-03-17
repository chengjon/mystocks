import type { DashboardMarketOverviewData } from '@/api/services/dashboardService'

export type DashboardMarketOverviewRecord = DashboardMarketOverviewData

function isDashboardMarketOverviewRecord(value: unknown): value is DashboardMarketOverviewRecord {
  if (!value || typeof value !== 'object') {
    return false
  }

  const candidate = value as Record<string, unknown>
  return Array.isArray(candidate.indices)
}

export function extractDashboardMarketOverview(payload: unknown): DashboardMarketOverviewRecord | null {
  if (isDashboardMarketOverviewRecord(payload)) {
    return payload
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>
    if (isDashboardMarketOverviewRecord(candidate.data)) {
      return candidate.data
    }
  }

  return null
}

export function extractDashboardRequestMeta(payload: unknown): {
  requestId: string
  processTime: string
} {
  if (!payload || typeof payload !== 'object') {
    return {
      requestId: '',
      processTime: ''
    }
  }

  const candidate = payload as Record<string, unknown>

  return {
    requestId: typeof candidate.request_id === 'string' ? candidate.request_id : '',
    processTime: typeof candidate.process_time === 'string' ? candidate.process_time : ''
  }
}
