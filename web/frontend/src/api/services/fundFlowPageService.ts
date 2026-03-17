import { apiGet } from '../apiClient.ts'
import type { UnifiedResponse } from '../types/common.ts'

export const FUND_FLOW_PAGE_API_ROOT = '/akshare/market/fund-flow' as const

export const FUND_FLOW_TIMEFRAME_DAYS = {
  today: 1,
  '3day': 3,
  '5day': 5,
  '10day': 10
} as const

export type FundFlowTimeframe = keyof typeof FUND_FLOW_TIMEFRAME_DAYS

interface RawListPayload {
  data?: Array<Record<string, unknown>>
  count?: number
}

export interface FundFlowSummaryRow {
  date: string
  northMoney: number
  southMoney: number
}

export interface FundFlowBigDealRow {
  symbol: string
  name: string
  bigDealAmount: number
  bigDealBuyAmount: number
  bigDealSellAmount: number
  bigDealNetInflow: number
}

export interface FundFlowPageSnapshot {
  timeframe: FundFlowTimeframe
  summaryRows: FundFlowSummaryRow[]
  rankingRows: FundFlowBigDealRow[]
}

function createEmptyResponse(
  message: string,
  requestId = '',
  processTime = '',
  errors?: unknown
): UnifiedResponse<FundFlowPageSnapshot> {
  return {
    success: false,
    code: 500,
    message,
    data: {
      timeframe: 'today',
      summaryRows: [],
      rankingRows: []
    },
    timestamp: new Date().toISOString(),
    request_id: requestId,
    process_time: processTime,
    errors
  }
}

function toNumber(value: unknown): number {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : 0
  }

  if (typeof value === 'string') {
    const normalized = value.replace(/,/g, '').trim()
    const parsed = Number.parseFloat(normalized)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function toDateString(value: unknown): string {
  if (typeof value === 'string' && value.trim()) {
    return value.slice(0, 10)
  }

  return ''
}

function pickValue(record: Record<string, unknown>, keys: string[]): unknown {
  for (const key of keys) {
    if (key in record && record[key] != null) {
      return record[key]
    }
  }

  return undefined
}

function extractRows(payload: RawListPayload | Array<Record<string, unknown>> | null | undefined): Array<Record<string, unknown>> {
  if (Array.isArray(payload)) {
    return payload
  }

  if (payload && Array.isArray(payload.data)) {
    return payload.data
  }

  return []
}

function normalizeSummaryRows(payload: RawListPayload | Array<Record<string, unknown>> | null | undefined): FundFlowSummaryRow[] {
  return extractRows(payload)
    .map((record) => ({
      date: toDateString(pickValue(record, ['date', '日期'])),
      northMoney: toNumber(pickValue(record, ['north_money', 'northMoney', '北向资金', 'north_total'])),
      southMoney: toNumber(pickValue(record, ['south_money', 'southMoney', '南向资金', 'south_total']))
    }))
    .filter((record) => record.date)
    .sort((left, right) => left.date.localeCompare(right.date))
}

function normalizeBigDealRows(payload: RawListPayload | Array<Record<string, unknown>> | null | undefined): FundFlowBigDealRow[] {
  return extractRows(payload)
    .map((record) => ({
      symbol: String(pickValue(record, ['symbol', '股票代码', 'code']) ?? ''),
      name: String(pickValue(record, ['name', '股票名称', 'stock_name']) ?? ''),
      bigDealAmount: toNumber(pickValue(record, ['big_deal_amount', '大单成交金额'])),
      bigDealBuyAmount: toNumber(pickValue(record, ['big_deal_buy_amount', '大单买入金额'])),
      bigDealSellAmount: toNumber(pickValue(record, ['big_deal_sell_amount', '大单卖出金额'])),
      bigDealNetInflow: toNumber(pickValue(record, ['big_deal_net_inflow', '大单净流入']))
    }))
    .filter((record) => record.symbol || record.name)
}

function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')

  return `${year}-${month}-${day}`
}

function buildDateRange(timeframe: FundFlowTimeframe): { startDate: string; endDate: string } {
  const days = FUND_FLOW_TIMEFRAME_DAYS[timeframe]
  const endDate = new Date()
  const startDate = new Date(endDate)

  startDate.setDate(endDate.getDate() - (days - 1))

  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  }
}

function filterSummaryRowsByRange(
  rows: FundFlowSummaryRow[],
  startDate: string,
  endDate: string
): FundFlowSummaryRow[] {
  return rows.filter((row) => row.date >= startDate && row.date <= endDate)
}

export const fundFlowPageService = {
  async getFundFlowPageSnapshot(
    options: {
      timeframe?: FundFlowTimeframe
    } = {}
  ): Promise<UnifiedResponse<FundFlowPageSnapshot>> {
    const timeframe = options.timeframe ?? 'today'
    const { startDate, endDate } = buildDateRange(timeframe)

    const [summaryResponse, rankingResponse] = await Promise.all([
      apiGet<UnifiedResponse<RawListPayload>>(`${FUND_FLOW_PAGE_API_ROOT}/hsgt-summary`, {
        start_date: startDate,
        end_date: endDate
      }),
      apiGet<UnifiedResponse<RawListPayload>>(`${FUND_FLOW_PAGE_API_ROOT}/big-deal`)
    ])

    if (!summaryResponse.success) {
      return createEmptyResponse(
        summaryResponse.message || '资金流向汇总加载失败',
        summaryResponse.request_id,
        summaryResponse.process_time,
        summaryResponse.errors
      )
    }

    if (!rankingResponse.success) {
      return createEmptyResponse(
        rankingResponse.message || '资金流向排行加载失败',
        rankingResponse.request_id,
        rankingResponse.process_time,
        rankingResponse.errors
      )
    }

    return {
      success: true,
      code: 200,
      message: 'ok',
      data: {
        timeframe,
        summaryRows: filterSummaryRowsByRange(
          normalizeSummaryRows(summaryResponse.data),
          startDate,
          endDate
        ),
        rankingRows: normalizeBigDealRows(rankingResponse.data)
      },
      timestamp: rankingResponse.timestamp || summaryResponse.timestamp || new Date().toISOString(),
      request_id: [summaryResponse.request_id, rankingResponse.request_id].filter(Boolean).join(' | '),
      process_time: [summaryResponse.process_time, rankingResponse.process_time].filter(Boolean).join(' | '),
      errors: null
    }
  }
}

export default fundFlowPageService
