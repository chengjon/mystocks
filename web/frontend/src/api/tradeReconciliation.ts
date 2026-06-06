import { request } from '@/utils/request.ts'

type ApiEnvelope<T> = {
  data?: T
  request_id?: string
}

export type ReconciliationImportSourceType = 'normalized_template' | 'miniqmt'
export type ReconciliationMatchStatus = 'matched' | 'mismatched' | 'missing_broker_record'

export interface ReconciliationAccountDescriptor {
  accountId: string
  label: string
  accountType: string
}

export interface ReconciliationStatementRow {
  accountId: string
  tradeId: string
  orderId: string
  symbol: string
  direction: string
  tradeTime: string
  price: number
  quantity: number
  amount: number
  commission: number
}

export interface ReconciliationStatementSummary {
  totalCount: number
  totalAmount: number
  totalCommission: number
}

export interface ReconciliationStatementsPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  verifiedAt: string
  accountId: string
  items: ReconciliationStatementRow[]
  summary: ReconciliationStatementSummary
  totalCount: number
  page: number
  pageSize: number
  source: string
}

export interface ReconciliationImportBatchPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  importBatchId: string
  accountId: string | null
  sourceType: ReconciliationImportSourceType
  rowCount: number
}

export interface BrokerReconciliationRow {
  accountId: string
  tradeId: string
  orderId: string
  symbol: string
  direction: string
  tradeTime: string
  price: number
  quantity: number
  amount: number
  commission: number
  sourceType: string
  rawRowNumber: number
}

export interface ReconciliationResultRow {
  matchStatus: ReconciliationMatchStatus
  internalRow: ReconciliationStatementRow
  brokerRow: BrokerReconciliationRow | null
  mismatchFields: string[]
}

export interface ReconciliationResultsPayload {
  status: string
  endpoint: string
  resource: string
  requestId: string
  verifiedAt: string
  accountId: string
  importBatchId: string
  items: ReconciliationResultRow[]
  totalCount: number
  page: number
  pageSize: number
  source: string
  matchStatus: ReconciliationMatchStatus | null
}

const RECONCILIATION_BASE_URL = '/trade/reconciliation'

const unwrapResponseData = <T>(raw: unknown): T => {
  if (raw && typeof raw === 'object' && 'data' in (raw as Record<string, unknown>)) {
    const outer = raw as ApiEnvelope<T>
    if (outer.data !== undefined) {
      return outer.data
    }
  }

  return raw as T
}

const asRecord = (value: unknown): Record<string, unknown> =>
  typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}

const asArray = <T = unknown>(value: unknown): T[] => Array.isArray(value) ? (value as T[]) : []

const asNumber = (value: unknown, fallback = 0): number =>
  typeof value === 'number' && Number.isFinite(value)
    ? value
    : typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))
      ? Number(value)
      : fallback

const asString = (value: unknown, fallback = ''): string =>
  typeof value === 'string' ? value : value == null ? fallback : String(value)

const extractEnvelopeRequestId = (raw: unknown): string => {
  if (raw && typeof raw === 'object' && 'request_id' in (raw as Record<string, unknown>)) {
    return asString((raw as Record<string, unknown>).request_id)
  }

  const outer = asRecord(raw)
  if ('data' in outer && outer.data && typeof outer.data === 'object' && 'request_id' in (outer.data as Record<string, unknown>)) {
    return asString((outer.data as Record<string, unknown>).request_id)
  }

  return ''
}

const asNullableString = (value: unknown): string | null =>
  value == null ? null : asString(value)

const unwrapTradeEnvelopeData = <T>(raw: unknown): T => {
  const payload = unwrapResponseData<unknown>(raw)
  const record = asRecord(payload)

  if ('data' in record && record.data !== undefined) {
    return record.data as T
  }

  return payload as T
}

const normalizeReconciliationStatementRow = (raw: unknown): ReconciliationStatementRow => {
  const record = asRecord(raw)
  return {
    accountId: asString(record.account_id),
    tradeId: asString(record.trade_id),
    orderId: asString(record.order_id),
    symbol: asString(record.symbol),
    direction: asString(record.direction),
    tradeTime: asString(record.trade_time),
    price: asNumber(record.price),
    quantity: asNumber(record.quantity),
    amount: asNumber(record.amount),
    commission: asNumber(record.commission),
  }
}

const normalizeBrokerReconciliationRow = (raw: unknown): BrokerReconciliationRow => {
  const record = asRecord(raw)
  return {
    accountId: asString(record.account_id),
    tradeId: asString(record.trade_id),
    orderId: asString(record.order_id),
    symbol: asString(record.symbol),
    direction: asString(record.direction),
    tradeTime: asString(record.trade_time),
    price: asNumber(record.price),
    quantity: asNumber(record.quantity),
    amount: asNumber(record.amount),
    commission: asNumber(record.commission),
    sourceType: asString(record.source_type),
    rawRowNumber: asNumber(record.raw_row_number),
  }
}

const normalizeReconciliationAccounts = (raw: unknown): ReconciliationAccountDescriptor[] => {
  const payload = unwrapTradeEnvelopeData<{ items?: unknown[] }>(raw)
  return asArray(payload?.items).map((item) => {
    const record = asRecord(item)
    return {
      accountId: asString(record.account_id),
      label: asString(record.label),
      accountType: asString(record.account_type),
    }
  })
}

const normalizeReconciliationStatements = (raw: unknown): ReconciliationStatementsPayload => {
  const payload = unwrapTradeEnvelopeData<Record<string, unknown>>(raw)
  const summary = asRecord(payload.summary)
  const requestId = extractEnvelopeRequestId(raw)
  const verifiedAt = requestId ? new Date().toISOString() : ''

  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'reconciliation_statements'),
    requestId,
    verifiedAt,
    accountId: asString(payload.account_id),
    items: asArray(payload.items).map(normalizeReconciliationStatementRow),
    summary: {
      totalCount: asNumber(summary.total_count),
      totalAmount: asNumber(summary.total_amount),
      totalCommission: asNumber(summary.total_commission),
    },
    totalCount: asNumber(payload.total_count),
    page: asNumber(payload.page, 1),
    pageSize: asNumber(payload.page_size, 20),
    source: asString(payload.source),
  }
}

const normalizeReconciliationImportBatch = (raw: unknown): ReconciliationImportBatchPayload => {
  const payload = unwrapTradeEnvelopeData<Record<string, unknown>>(raw)
  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'reconciliation_import_batch'),
    requestId: extractEnvelopeRequestId(raw),
    importBatchId: asString(payload.import_batch_id),
    accountId: asNullableString(payload.account_id),
    sourceType: asString(payload.source_type, 'normalized_template') as ReconciliationImportSourceType,
    rowCount: asNumber(payload.row_count),
  }
}

const normalizeReconciliationResults = (raw: unknown): ReconciliationResultsPayload => {
  const payload = unwrapTradeEnvelopeData<Record<string, unknown>>(raw)
  const requestId = extractEnvelopeRequestId(raw)
  const verifiedAt = requestId ? new Date().toISOString() : ''

  return {
    status: asString(payload.status, 'available'),
    endpoint: asString(payload.endpoint, 'trade'),
    resource: asString(payload.resource, 'reconciliation_results'),
    requestId,
    verifiedAt,
    accountId: asString(payload.account_id),
    importBatchId: asString(payload.import_batch_id),
    items: asArray(payload.items).map((item) => {
      const record = asRecord(item)
      return {
        matchStatus: asString(record.match_status) as ReconciliationMatchStatus,
        internalRow: normalizeReconciliationStatementRow(record.internal_row),
        brokerRow: record.broker_row ? normalizeBrokerReconciliationRow(record.broker_row) : null,
        mismatchFields: asArray<string>(record.mismatch_fields),
      }
    }),
    totalCount: asNumber(payload.total_count),
    page: asNumber(payload.page, 1),
    pageSize: asNumber(payload.page_size, 20),
    source: asString(payload.source),
    matchStatus: asNullableString(payload.match_status) as ReconciliationMatchStatus | null,
  }
}

export const fetchReconciliationAccounts = async (): Promise<ReconciliationAccountDescriptor[]> => {
  const rawData = await request.get(`${RECONCILIATION_BASE_URL}/accounts`)
  return normalizeReconciliationAccounts(rawData)
}

export const fetchReconciliationStatements = async (params: {
  accountId: string
  startDate?: string
  endDate?: string
  page?: number
  pageSize?: number
}): Promise<ReconciliationStatementsPayload> => {
  const rawData = await request.get(`${RECONCILIATION_BASE_URL}/statements`, {
    params: {
      account_id: params.accountId,
      start_date: params.startDate,
      end_date: params.endDate,
      page: params.page,
      page_size: params.pageSize,
    },
  })
  return normalizeReconciliationStatements(rawData)
}

export const uploadReconciliationCsv = async (params: {
  file: File
  sourceType: ReconciliationImportSourceType
  accountId?: string
}): Promise<ReconciliationImportBatchPayload> => {
  const formData = new FormData()
  formData.append('file', params.file)
  formData.append('source_type', params.sourceType)

  if (params.accountId) {
    formData.append('account_id', params.accountId)
  }

  const rawData = await request.post(`${RECONCILIATION_BASE_URL}/import`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return normalizeReconciliationImportBatch(rawData)
}

export const fetchReconciliationResults = async (params: {
  accountId: string
  importBatchId: string
  startDate?: string
  endDate?: string
  matchStatus?: ReconciliationMatchStatus
  page?: number
  pageSize?: number
}): Promise<ReconciliationResultsPayload> => {
  const rawData = await request.get(`${RECONCILIATION_BASE_URL}/results`, {
    params: {
      account_id: params.accountId,
      import_batch_id: params.importBatchId,
      start_date: params.startDate,
      end_date: params.endDate,
      match_status: params.matchStatus,
      page: params.page,
      page_size: params.pageSize,
    },
  })
  return normalizeReconciliationResults(rawData)
}

export const downloadReconciliationResults = async (params: {
  accountId: string
  importBatchId: string
  startDate?: string
  endDate?: string
  matchStatus?: ReconciliationMatchStatus
}): Promise<Blob> => {
  const response = await request.get(`${RECONCILIATION_BASE_URL}/export`, {
    params: {
      account_id: params.accountId,
      import_batch_id: params.importBatchId,
      start_date: params.startDate,
      end_date: params.endDate,
      match_status: params.matchStatus,
    },
    responseType: 'blob',
  })

  if (response instanceof Blob) {
    return response
  }

  const responseRecord = asRecord(response)
  if (responseRecord.data instanceof Blob) {
    return responseRecord.data
  }

  return response as Blob
}
