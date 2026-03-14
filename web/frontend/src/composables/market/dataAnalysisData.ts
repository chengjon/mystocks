export interface DataAnalysisIndicatorItem {
  id: number
  name: string
  key: string
  category: string
  categoryLabel: string
  type: '主图' | '副图'
  description: string
  params: unknown[]
}

export interface DataAnalysisStatsInput {
  indicators: Array<unknown>
  stockUniverseSize: number
  qualifiedStocks: number
  previousQualifiedStocks: number
  screeningTimes: number
}

export interface StockScreeningResultRow {
  symbol: string
  name: string
  price: number
  changePercent: number
  volume: number
  amount: number
  pe: number
  marketCap: number
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function parseString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value.trim().length > 0 ? value : fallback
}

function extractIndicatorRows(raw: unknown): Record<string, unknown>[] {
  if (!isRecord(raw)) {
    return []
  }

  if (Array.isArray(raw.indicators)) {
    return raw.indicators.filter(isRecord)
  }

  if (isRecord(raw.data) && Array.isArray(raw.data.indicators)) {
    return raw.data.indicators.filter(isRecord)
  }

  return []
}

function toCategoryLabel(category: string): string {
  return (
    {
      trend: '趋势',
      momentum: '动量',
      volatility: '波动',
      volume: '成交量',
      candlestick: '形态',
    }[category] || '其他'
  )
}

export function extractDataAnalysisIndicators(raw: unknown): DataAnalysisIndicatorItem[] {
  return extractIndicatorRows(raw).map((row, index) => {
    const key = parseString(row.abbreviation, `indicator-${index + 1}`).toLowerCase()
    const category = parseString(row.category, 'trend')
    const panelType = parseString(row.panel_type, parseString(row.panelType, 'overlay'))

    return {
      id: index + 1,
      name: parseString(row.chinese_name, parseString(row.chineseName, parseString(row.full_name, key.toUpperCase()))),
      key,
      category,
      categoryLabel: toCategoryLabel(category),
      type: panelType === 'overlay' ? '主图' : '副图',
      description: parseString(row.description, '暂无说明'),
      params: Array.isArray(row.parameters) ? row.parameters : [],
    }
  })
}

export function buildDataAnalysisStats(input: DataAnalysisStatsInput) {
  return {
    availableIndicators: input.indicators.length,
    customIndicators: 0,
    screenedStocks: input.stockUniverseSize,
    screeningTimes: input.screeningTimes,
    qualifiedStocks: input.qualifiedStocks,
    qualifiedChange: input.qualifiedStocks - input.previousQualifiedStocks,
  }
}

export function toDataAnalysisResults(rows: StockScreeningResultRow[]) {
  return rows.map((row) => ({
    symbol: row.symbol,
    name: row.name,
    price: row.price,
    change: row.changePercent,
    volume: row.volume,
    amount: row.amount,
    pe: row.pe,
    marketCap: row.marketCap,
  }))
}
