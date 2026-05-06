import type {
  ReconciliationAccountDescriptor,
  ReconciliationMatchStatus,
  ReconciliationResultsPayload,
  ReconciliationStatementsPayload,
} from '@/api/trade'

export interface ReconciliationAccountOption {
  value: string
  label: string
  accountType: string
}

export interface ReconciliationSummarySnapshot {
  totalCount: string
  totalAmount: string
  totalCommission: string
}

export interface ReconciliationResultMetrics {
  matched: number
  mismatched: number
  missingBrokerRecord: number
}

export interface ReconciliationResultDisplayRow {
  key: string
  symbol: string
  directionText: string
  tradeTime: string
  amountText: string
  commissionText: string
  status: ReconciliationMatchStatus
  statusText: string
  brokerSourceText: string
  mismatchSummary: string
}

const STATUS_TEXT: Record<ReconciliationMatchStatus, string> = {
  matched: '已匹配',
  mismatched: '差异',
  missing_broker_record: '缺少券商记录',
}

const DIRECTION_TEXT: Record<string, string> = {
  buy: '买入',
  sell: '卖出',
}

const SOURCE_TEXT: Record<string, string> = {
  normalized_template: '统一模板',
  miniqmt: 'miniQMT',
}

const numberFormatter = new Intl.NumberFormat('zh-CN', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export const formatReconciliationNumber = (value: number): string => numberFormatter.format(value)

export const formatReconciliationTimestamp = (value: string): string => {
  if (!value) {
    return 'N/A'
  }

  const normalized = value.includes('T') ? value : value.replace(' ', 'T')
  const date = new Date(normalized)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return normalized.slice(0, 19).replace('T', ' ')
}

export const toReconciliationAccountOptions = (
  accounts: ReconciliationAccountDescriptor[],
): ReconciliationAccountOption[] => accounts.map((account) => ({
  value: account.accountId,
  label: account.label,
  accountType: account.accountType,
}))

export const toReconciliationSummarySnapshot = (
  payload: ReconciliationStatementsPayload | null,
): ReconciliationSummarySnapshot => ({
  totalCount: payload ? String(payload.summary.totalCount) : '--',
  totalAmount: payload ? formatReconciliationNumber(payload.summary.totalAmount) : '--',
  totalCommission: payload ? formatReconciliationNumber(payload.summary.totalCommission) : '--',
})

export const toReconciliationResultMetrics = (
  payload: ReconciliationResultsPayload | null,
): ReconciliationResultMetrics => {
  const metrics: ReconciliationResultMetrics = {
    matched: 0,
    mismatched: 0,
    missingBrokerRecord: 0,
  }

  if (!payload) {
    return metrics
  }

  payload.items.forEach((item) => {
    if (item.matchStatus === 'matched') {
      metrics.matched += 1
    } else if (item.matchStatus === 'mismatched') {
      metrics.mismatched += 1
    } else {
      metrics.missingBrokerRecord += 1
    }
  })

  return metrics
}

export const toReconciliationResultRows = (
  payload: ReconciliationResultsPayload | null,
): ReconciliationResultDisplayRow[] => {
  if (!payload) {
    return []
  }

  return payload.items.map((item) => ({
    key: item.internalRow.tradeId,
    symbol: item.internalRow.symbol,
    directionText: DIRECTION_TEXT[item.internalRow.direction] || item.internalRow.direction,
    tradeTime: formatReconciliationTimestamp(item.internalRow.tradeTime),
    amountText: formatReconciliationNumber(item.internalRow.amount),
    commissionText: formatReconciliationNumber(item.internalRow.commission),
    status: item.matchStatus,
    statusText: STATUS_TEXT[item.matchStatus],
    brokerSourceText: item.brokerRow ? (SOURCE_TEXT[item.brokerRow.sourceType] || item.brokerRow.sourceType) : '缺失',
    mismatchSummary: item.mismatchFields.length > 0 ? item.mismatchFields.join(', ') : '—',
  }))
}
