export interface FundChannel {
  amount: number
  change: number
}

export interface FundData {
  shanghai: FundChannel
  shenzhen: FundChannel
  north: FundChannel
  main: FundChannel
}

export interface TrendItem {
  date: string
  value: number
}

export interface StockRankingRow {
  rank: number
  name: string
  code: string
  price: number
  change: number
  inflow: string
  mainForce: string
}

interface HsgtSummaryRow {
  交易日?: unknown
  板块?: unknown
  资金方向?: unknown
  成交净买额?: unknown
  指数涨跌幅?: unknown
}

interface BigDealRow {
  symbol?: unknown
  股票简称?: unknown
  成交价格?: unknown
  成交额?: unknown
  大单性质?: unknown
  涨跌幅?: unknown
}

function parseNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string' && value.trim()) {
    const cleaned = value.replace('%', '')
    const parsed = Number.parseFloat(cleaned)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function normalizeAmountToYi(value: number): number {
  const absValue = Math.abs(value)
  if (absValue > 10000) {
    return value / 100000000
  }
  return value
}

function yi(value: number): number {
  return Number(normalizeAmountToYi(value).toFixed(2))
}

function signedYi(value: number): string {
  const yiValue = yi(value)
  const prefix = yiValue > 0 ? '+' : ''
  return `${prefix}${yiValue.toFixed(2)}`
}

function extractRows<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[]
  }

  if (payload && typeof payload === 'object') {
    const candidate = payload as { data?: unknown }
    if (Array.isArray(candidate.data)) {
      return candidate.data as T[]
    }
  }

  return []
}

export function buildFundOverview(summaryPayload: unknown, bigDealPayload: unknown): FundData {
  const summaryRows = extractRows<HsgtSummaryRow>(summaryPayload)
  const bigDealRows = extractRows<BigDealRow>(bigDealPayload)

  const shanghaiRow = summaryRows.find((row) => row.板块 === '沪股通')
  const shenzhenRow = summaryRows.find((row) => row.板块 === '深股通')
  const northRows = summaryRows.filter((row) => row.资金方向 === '北向')

  const northAmount = northRows.reduce((sum, row) => sum + parseNumber(row.成交净买额), 0)
  const northChange = northRows.length
    ? northRows.reduce((sum, row) => sum + parseNumber(row.指数涨跌幅), 0) / northRows.length
    : 0

  const mainAmount = bigDealRows.reduce((sum, row) => {
    const amount = parseNumber(row.成交额)
    const direction = row.大单性质 === '卖盘' ? -1 : 1
    return sum + amount * direction
  }, 0)

  return {
    shanghai: {
      amount: parseNumber(shanghaiRow?.成交净买额),
      change: parseNumber(shanghaiRow?.指数涨跌幅),
    },
    shenzhen: {
      amount: parseNumber(shenzhenRow?.成交净买额),
      change: parseNumber(shenzhenRow?.指数涨跌幅),
    },
    north: {
      amount: northAmount,
      change: Number(northChange.toFixed(2)),
    },
    main: {
      amount: mainAmount,
      change: 0,
    },
  }
}

export function buildFundTrend(summaryPayload: unknown): TrendItem[] {
  const summaryRows = extractRows<HsgtSummaryRow>(summaryPayload)
  const grouped = new Map<string, number>()

  for (const row of summaryRows) {
    const date = typeof row.交易日 === 'string' ? row.交易日 : ''
    if (!date || row.资金方向 !== '北向') {
      continue
    }
    grouped.set(date, (grouped.get(date) || 0) + parseNumber(row.成交净买额))
  }

  return [...grouped.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .slice(-30)
    .map(([date, value]) => ({ date, value: yi(value) }))
}

export function buildStockRanking(bigDealPayload: unknown): StockRankingRow[] {
  const rows = extractRows<BigDealRow>(bigDealPayload)

  return rows.slice(0, 20).map((row, index) => {
    const amount = parseNumber(row.成交额)
    const direction = row.大单性质 === '卖盘' ? -1 : 1
    return {
      rank: index + 1,
      name: typeof row.股票简称 === 'string' ? row.股票简称 : `股票-${index + 1}`,
      code: String(row.symbol ?? 'N/A'),
      price: parseNumber(row.成交价格),
      change: parseNumber(row.涨跌幅),
      inflow: signedYi(amount * direction),
      mainForce: signedYi(amount * direction),
    }
  })
}
