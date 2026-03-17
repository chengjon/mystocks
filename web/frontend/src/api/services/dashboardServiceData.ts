import type {
  FundFlowData,
  IndustryFlowData,
  MarketOverviewData,
  PositionRiskData,
  StockFlowRankingData,
  SystemHealthData,
} from "./dashboardService.ts"

function unwrapDashboardPayload(payload: unknown): unknown {
  if (payload && typeof payload === "object" && "data" in (payload as Record<string, unknown>)) {
    return (payload as Record<string, unknown>).data
  }
  return payload
}

function extractRows(payload: unknown): Record<string, unknown>[] {
  const unwrapped = unwrapDashboardPayload(payload)

  if (Array.isArray(unwrapped)) {
    return unwrapped as Record<string, unknown>[]
  }

  if (unwrapped && typeof unwrapped === "object") {
    const candidate = unwrapped as Record<string, unknown>
    const collections = [
      candidate.data,
      candidate.items,
      candidate.records,
      candidate.quotes,
      candidate.positions,
      candidate.indices,
    ]

    for (const collection of collections) {
      if (Array.isArray(collection)) {
        return collection as Record<string, unknown>[]
      }
      if (collection && typeof collection === "object") {
        const nested = collection as Record<string, unknown>
        if (Array.isArray(nested.data)) {
          return nested.data as Record<string, unknown>[]
        }
        if (Array.isArray(nested.items)) {
          return nested.items as Record<string, unknown>[]
        }
      }
    }
  }

  return []
}

function toNumber(value: unknown, fallback = 0): number {
  const numeric = typeof value === "string" ? Number.parseFloat(value.replace("%", "")) : Number(value)
  return Number.isFinite(numeric) ? numeric : fallback
}

function toYi(value: number): number {
  const normalized = Math.abs(value) > 10000 ? value / 100000000 : value
  return Number(normalized.toFixed(2))
}

export function normalizeDashboardMarketOverview(payload: unknown): MarketOverviewData[] {
  const nameBySymbol: Record<string, string> = {
    "000001.SH": "上证指数",
    "399001.SZ": "深证成指",
    "399006.SZ": "创业板指",
  }

  return extractRows(payload).map((row, index) => ({
    symbol: String(row.symbol ?? row.code ?? `IDX-${index + 1}`),
    name: String(
      nameBySymbol[String(row.symbol ?? row.code ?? "")] ??
      row.name ??
      row.display_name ??
      `指数-${index + 1}`
    ),
    latest_price: toNumber(row.latest_price ?? row.current_price ?? row.price),
    change_percent: toNumber(row.change_percent ?? row.change),
    volume: toNumber(row.volume ?? row.amount ?? row.total_turnover),
  }))
}

export function normalizeDashboardFundFlow(summaryPayload: unknown, bigDealPayload: unknown): FundFlowData {
  const summaryRows = extractRows(summaryPayload)
  const bigDealRows = extractRows(bigDealPayload)

  const shanghaiRow = summaryRows.find((row) => row["板块"] === "沪股通")
  const shenzhenRow = summaryRows.find((row) => row["板块"] === "深股通")
  const northRows = summaryRows.filter((row) => row["资金方向"] === "北向")

  const northAmount = northRows.reduce((sum, row) => sum + toNumber(row["成交净买额"]), 0)
  const northChange = northRows.length
    ? northRows.reduce((sum, row) => sum + toNumber(row["指数涨跌幅"]), 0) / northRows.length
    : 0

  const mainAmount = bigDealRows.reduce((sum, row) => {
    const amount = toNumber(row["成交额"] ?? row.amount)
    const direction = row["大单性质"] === "卖盘" ? -1 : 1
    return sum + amount * direction
  }, 0)

  return {
    hgt: {
      amount: toYi(toNumber(shanghaiRow?.["成交净买额"])),
      change: toNumber(shanghaiRow?.["指数涨跌幅"]),
    },
    sgt: {
      amount: toYi(toNumber(shenzhenRow?.["成交净买额"])),
      change: toNumber(shenzhenRow?.["指数涨跌幅"]),
    },
    northTotal: {
      amount: toYi(northAmount),
      monthly: toYi(northAmount),
    },
    mainForce: {
      amount: toYi(mainAmount),
      percentage: Number(northChange.toFixed(2)),
    },
  }
}

export function normalizeDashboardIndustryFlow(payload: unknown): IndustryFlowData[] {
  return extractRows(payload).map((row, index) => ({
    name: String(row.sector_name ?? row["名称"] ?? row["板块名称"] ?? row["行业名称"] ?? row.name ?? `板块-${index + 1}`),
    change: toNumber(row.change_percent ?? row["今日涨跌幅"] ?? row["涨跌幅"] ?? row.change),
    amount: toYi(toNumber(row.main_net_inflow ?? row["今日主力净流入-净额"] ?? row.amount)),
  }))
}

export function normalizeDashboardStockFlowRanking(payload: unknown): StockFlowRankingData[] {
  return extractRows(payload).slice(0, 20).map((row, index) => {
    const amount = toNumber(row["成交额"] ?? row.amount)
    const direction = row["大单性质"] === "卖盘" ? -1 : 1
    return {
      code: String(row.symbol ?? row.code ?? `STK-${index + 1}`),
      name: String(row["股票简称"] ?? row.name ?? `股票-${index + 1}`),
      amount: toYi(amount * direction),
      change: toNumber(row["涨跌幅"] ?? row.change),
    }
  })
}

export function normalizeDashboardActiveStrategies(payload: unknown): Record<string, unknown>[] {
  return extractRows(payload)
}

export function normalizeDashboardPositionRisk(payload: unknown): PositionRiskData {
  const data = unwrapDashboardPayload(payload) as Record<string, unknown> | undefined
  const positions = extractRows(data)
  const totalValue = toNumber(
    data?.total_market_value ?? data?.total_value,
    positions.reduce((sum, row) => sum + toNumber(row.market_value), 0),
  )
  const totalPnL = positions.reduce(
    (sum, row) =>
      sum +
      toNumber(row.unrealized_pnl ?? row.profit_loss) +
      toNumber(row.realized_pnl),
    0,
  )
  const maxWeight = positions.reduce((max, row) => {
    const explicitWeight = toNumber(row.weight, NaN)
    if (Number.isFinite(explicitWeight)) {
      return Math.max(max, explicitWeight)
    }
    const marketValue = toNumber(row.market_value)
    const estimatedWeight = totalValue > 0 ? marketValue / totalValue : 0
    return Math.max(max, estimatedWeight)
  }, 0)
  const riskLevel: PositionRiskData["riskLevel"] = maxWeight > 0.5 ? "high" : maxWeight > 0.25 ? "medium" : "low"

  return {
    totalValue,
    totalPnL,
    pnlPercent: totalValue > 0 ? Number(((totalPnL / totalValue) * 100).toFixed(2)) : 0,
    maxDrawdown: 0,
    riskLevel,
    riskLevelText: riskLevel === "high" ? "高风险" : riskLevel === "medium" ? "中风险" : "低风险",
  }
}

export function normalizeDashboardSystemHealth(payload: unknown): SystemHealthData[] {
  const data = unwrapDashboardPayload(payload) as Record<string, unknown> | undefined
  const status = String(data?.status ?? "unknown")
  const normalizedStatus: SystemHealthData["status"] =
    status === "healthy" ? "good" : status === "degraded" || status === "warning" ? "warning" : "error"

  return [
    { label: "服务状态", value: status.toUpperCase(), status: normalizedStatus },
    { label: "服务名称", value: String(data?.service ?? "N/A"), status: "good" },
    { label: "版本", value: String(data?.version ?? "N/A"), status: "good" },
  ]
}
