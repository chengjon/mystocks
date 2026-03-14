export interface IndustryFlowRow {
  rank?: number
  name?: string
  sector_name?: string
  change?: number | string
  change_percent?: number | string
  amount?: number | string
  main_net_inflow?: number | string
  main_net_inflow_rate?: number | string
}

export interface BoardRow {
  rank: number
  name: string
  change: string
  turnover: number
  netInflow: string
}

export interface RotationRow {
  name: string
  window: string
  flow: number
}

function parseNumeric(value: unknown): number {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : 0
  }
  return Number.parseFloat(String(value ?? '0')) || 0
}

function formatSigned(value: number, digits = 2): string {
  const normalized = Number.isFinite(value) ? value : 0
  const prefix = normalized > 0 ? '+' : ''
  return `${prefix}${normalized.toFixed(digits)}`
}

export function extractIndustryFlowRows(payload: unknown): IndustryFlowRow[] {
  if (Array.isArray(payload)) {
    return payload as IndustryFlowRow[]
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>
    const collections = [candidate.items, candidate.data, candidate.records]
    for (const collection of collections) {
      if (Array.isArray(collection)) {
        return collection as IndustryFlowRow[]
      }
    }
  }

  return []
}

export function toBoardRows(rows: IndustryFlowRow[]): BoardRow[] {
  return rows.map((row, index) => {
    const change = parseNumeric(row.change_percent ?? row.change)
    const netAmountRaw = parseNumeric(row.main_net_inflow)
    const hasV2NetAmount = Number.isFinite(netAmountRaw) && netAmountRaw !== 0
    const turnover = hasV2NetAmount ? Number((netAmountRaw / 100000000).toFixed(2)) : parseNumeric(row.amount)
    const netInflowRate = parseNumeric(row.main_net_inflow_rate)

    return {
      rank: typeof row.rank === 'number' ? row.rank : index + 1,
      name:
        (typeof row.name === 'string' && row.name.trim().length > 0
          ? row.name
          : typeof row.sector_name === 'string' && row.sector_name.trim().length > 0
            ? row.sector_name
            : `板块-${index + 1}`),
      change: `${formatSigned(change)}%`,
      turnover: Number(turnover.toFixed(2)),
      netInflow: hasV2NetAmount ? `${formatSigned(netInflowRate)}%` : formatSigned(turnover * (change / 100), 1)
    }
  })
}

export function toRotationRows(rows: BoardRow[]): RotationRow[] {
  const windows = ['近1日', '近3日', '近5日', '近10日']
  return rows.slice(0, 4).map((row, index) => ({
    name: row.name,
    window: windows[index] ?? '近1日',
    flow: row.turnover
  }))
}
