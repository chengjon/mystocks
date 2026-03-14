export interface ConceptRow {
  name: string
  change_pct: number
  main_inflow: string
  leader: string
}

interface ConceptApiItem {
  sector_name?: unknown
  name?: unknown
  change_percent?: unknown
  change_pct?: unknown
  main_net_inflow?: unknown
  main_inflow?: unknown
  leading_stock?: unknown
  leader?: unknown
}

export function buildConceptRequest(): {
  path: string
  params: Record<string, unknown>
} {
  return {
    path: "/v2/market/sector/fund-flow",
    params: {
      sector_type: "概念",
      timeframe: "今日",
      limit: 20,
    },
  }
}

function parseNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value
  }

  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function formatYi(value: number): string {
  const yi = value / 100000000
  const prefix = yi > 0 ? "+" : ""
  return `${prefix}${yi.toFixed(1)}亿`
}

export function extractConceptRows(payload: unknown): ConceptRow[] {
  const rows = Array.isArray(payload) ? (payload as ConceptApiItem[]) : []

  return rows.map((row, index) => ({
    name:
      (typeof row.sector_name === "string" && row.sector_name) ||
      (typeof row.name === "string" && row.name) ||
      `概念-${index + 1}`,
    change_pct: parseNumber(row.change_percent ?? row.change_pct),
    main_inflow: formatYi(parseNumber(row.main_net_inflow ?? row.main_inflow)),
    leader:
      (typeof row.leading_stock === "string" && row.leading_stock) ||
      (typeof row.leader === "string" && row.leader) ||
      "N/A",
  }))
}
